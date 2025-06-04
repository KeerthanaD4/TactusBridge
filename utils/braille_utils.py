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


def text_to_braille_image(text, max_chars_per_line=20):
    text = text.lower()
    braille_output = ''
    braille_patterns = []

    for char in text:
        pattern = braille_dict.get(char, '000000')
        braille_patterns.append(pattern)
        braille_output += pattern + ' '

    dot_radius = 12
    dot_spacing = 30
    char_spacing = 40

    cell_width = 2 * dot_spacing
    cell_height = 3 * dot_spacing

    lines = [braille_patterns[i:i+max_chars_per_line] for i in range(0, len(braille_patterns), max_chars_per_line)]
    num_lines = len(lines)

    img_width = max_chars_per_line * (cell_width + char_spacing)
    img_height = num_lines * (cell_height + 40)

    # 🔁 Background = black
    img = Image.new("RGB", (img_width, img_height), "black")
    draw = ImageDraw.Draw(img)

    for row_idx, line in enumerate(lines):
        for col_idx, pattern in enumerate(line):
            x_offset = col_idx * (cell_width + char_spacing)
            y_offset = row_idx * (cell_height + 40)
            for j, dot in enumerate(pattern):
                if dot == '1':
                    dx = x_offset + (j % 2) * dot_spacing
                    dy = y_offset + (j // 2) * dot_spacing
                    # 🔁 Draw white dots
                    draw.ellipse([dx, dy, dx + dot_radius, dy + dot_radius], fill="white")

    output_path = "static/braille_output.png"
    img.save(output_path)
    return braille_output.strip(), output_path

def braille_image_to_text(image_path):
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

    dots.sort(key=lambda p: p[0])  # sort left to right

    def group_dots_by_distance(dots, threshold=60):
        clusters = []
        current = []

        for i, (x, y) in enumerate(dots):
            if not current:
                current.append((x, y))
            else:
                last_x, _ = current[-1]
                if abs(x - last_x) <= threshold:
                    current.append((x, y))
                else:
                    clusters.append(current)
                    current = [(x, y)]
        if current:
            clusters.append(current)
        return clusters

    clusters = group_dots_by_distance(dots)
    cells = [cluster for cluster in clusters if len(cluster) == 6]

    output_text = ""
    braille_output = ""

    for cell in cells:
        xs, ys = zip(*cell)
        min_x, min_y = min(xs), min(ys)
        norm = [(x - min_x, y - min_y) for x, y in cell]

        w = max(x for x, _ in norm)
        h = max(y for _, y in norm)
        if w == 0 or h == 0:
            continue

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

    output_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    for (x, y) in dots:
        cv2.circle(output_img, (x, y), 5, (0, 0, 255), -1)
    cv2.imwrite("static/braille_output_debug.png", output_img)

    print(f"[DEBUG] Final Output — Text: '{output_text}', Braille: '{braille_output}'")
    return braille_output, output_text
