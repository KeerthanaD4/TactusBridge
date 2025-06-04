from PIL import Image, ImageDraw
import cv2
import numpy as np

braille_dict = {
    'a': '100000', 'b': '101000', 'c': '110000', 'd': '110100',
    'e': '100100', 'f': '111000', 'g': '111100', 'h': '101100',
    'i': '011000', 'j': '011100', 'k': '100010', 'l': '101010',
    'm': '110010', 'n': '110110', 'o': '100110', 'p': '111010',
    'q': '111110', 'r': '101110', 's': '011010', 't': '011110',
    'u': '100011', 'v': '101011', 'w': '011101', 'x': '110011',
    'y': '110111', 'z': '100111', ' ': '000000'
}
inverse_braille_dict = {v: k for k, v in braille_dict.items()}

def text_to_braille_image(text):
    text = text.lower()
    braille_output = ''.join(braille_dict.get(char, '000000') for char in text)

    dot_radius = 12
    dot_spacing = 30
    char_spacing = 40

    cell_width = 2 * dot_spacing
    cell_height = 3 * dot_spacing

    img_width = len(text) * (cell_width + char_spacing)
    img_height = cell_height + 40

    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    for i, char in enumerate(text):
        pattern = braille_dict.get(char, '000000')
        x_offset = i * (cell_width + char_spacing)
        for j, dot in enumerate(pattern):
            if dot == '1':
                dx = x_offset + (j % 2) * dot_spacing
                dy = 20 + (j // 2) * dot_spacing
                draw.ellipse([dx, dy, dx + dot_radius, dy + dot_radius], fill="black")

    output_path = "static/braille_output.png"
    img.save(output_path)
    return braille_output, output_path

def braille_image_to_text(image_path):
    import cv2
    import numpy as np
    from sklearn.cluster import KMeans

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Threshold
    thresh = cv2.adaptiveThreshold(img, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV,
                                   11, 3)

    cv2.imwrite("static/debug_thresh.png", thresh)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dots = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 20 < area < 1500:
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                dots.append((cx, cy))

    print(f"[DEBUG] Dots detected: {len(dots)}")

    if len(dots) < 6:
        return "", ""

    # Sort left to right
    dots.sort(key=lambda p: p[0])

    # Group into sets of 6 dots (naive chunking for now)
    cells = []
    for i in range(0, len(dots), 6):
        chunk = dots[i:i+6]
        if len(chunk) < 6:
            continue
        cells.append(chunk)

    output_text = ""
    braille_output = ""

    for cell in cells:
        # Normalize dots: top-left = (0,0), map others relative to it
        xs, ys = zip(*cell)
        min_x, min_y = min(xs), min(ys)
        norm = [(x - min_x, y - min_y) for x, y in cell]

        # Estimate average width/height of Braille cell
        w = max(x for x, _ in norm)
        h = max(y for _, y in norm)
        if w == 0 or h == 0:
            continue

        # Determine dot positions
        pattern = ['0'] * 6
        for x, y in norm:
            col = 0 if x < w / 2 else 1
            if y < h / 3:
                row = 0
            elif y < 2 * h / 3:
                row = 1
            else:
                row = 2
            index = row * 2 + col
            if index < 6:
                pattern[index] = '1'

        pattern_str = ''.join(pattern)
        char = inverse_braille_dict.get(pattern_str, '')
        print(f"[DEBUG] Cell pattern: {pattern_str} → {char or '[ignored]'}")

        output_text += char
        braille_output += pattern_str

    # Debug image
    output_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    for (x, y) in dots:
        cv2.circle(output_img, (x, y), 5, (0, 0, 255), -1)
    cv2.imwrite("static/braille_output_debug.png", output_img)

    print(f"[DEBUG] Final Output — Text: '{output_text}', Braille: '{braille_output}'")
    return braille_output, output_text
