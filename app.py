import os
from flask import Flask, render_template, request, send_file
from utils.braille_utils import braille_image_to_text, text_to_braille_image
from utils.speech_utils import text_to_speech, speech_to_text
import speech_recognition as sr
import ffmpeg

# Directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    braille_img_path = None
    speech_file = None

    if request.method == "POST":
        mode = request.form["mode"]

        if mode == "braille_to_text":
            image = request.files.get("image")
            if image:
                image_path = os.path.join(UPLOAD_FOLDER, image.filename)
                image.save(image_path)
                braille_text, normal_text = braille_image_to_text(image_path)
                print(f"[DEBUG] Extracted Text: '{normal_text}'")

                if normal_text.strip():
                    try:
                        speech_output_path = os.path.join(STATIC_FOLDER, "output.mp3")
                        text_to_speech(normal_text, speech_output_path)
                        speech_file = "output.mp3"
                    except Exception as e:
                        print(f"[ERROR] TTS failed: {e}")
                        speech_file = None
                else:
                    print(f"[WARN] No valid text extracted from image: '{normal_text}'")
                    speech_file = None

                result = f"Braille: {braille_text} | Text: {normal_text or '[No text detected]'}"
            else:
                result = "No image uploaded."

        elif mode == "speech_to_braille":
            text = speech_to_text()
            if text.strip():
                braille_text, img_path = text_to_braille_image(text)
                braille_img_path = img_path

                speech_output_path = os.path.join(STATIC_FOLDER, "output.mp3")
                text_to_speech(text, speech_output_path)
                speech_file = "output.mp3"

                result = f"Input Speech Text: {text} | Braille: {braille_text}"
            else:
                result = "Could not recognize any speech."

        elif mode == "speech_to_braille_audio":
            audio_file = request.files.get("audio")
            if audio_file:
                original_audio_path = os.path.join(UPLOAD_FOLDER, "speech.webm")
                audio_file.save(original_audio_path)

                converted_path = os.path.join(UPLOAD_FOLDER, "speech.wav")
                if not convert_to_wav(original_audio_path, converted_path):
                    result = "Failed to convert audio."
                    return render_template("index.html", result=result)

                recognizer = sr.Recognizer()
                with sr.AudioFile(converted_path) as source:
                    audio = recognizer.record(source)
                    try:
                        text = recognizer.recognize_google(audio)
                        print(f"[DEBUG] Audio speech: {text}")
                    except sr.UnknownValueError:
                        text = ""
                    except sr.RequestError:
                        text = ""

                if text.strip():
                    braille_text, img_path = text_to_braille_image(text)
                    braille_img_path = img_path

                    speech_output_path = os.path.join(STATIC_FOLDER, "output.mp3")
                    text_to_speech(text, speech_output_path)
                    speech_file = "output.mp3"

                    result = f"Input Speech Text: {text} | Braille: {braille_text}"
                else:
                    result = "Could not recognize speech from uploaded audio."
            else:
                result = "No audio file uploaded."

        elif mode == "text_to_braille":
            text = request.form.get("text")
            if text:
                braille_text, img_path = text_to_braille_image(text)
                braille_img_path = img_path

                speech_output_path = os.path.join(STATIC_FOLDER, "output.mp3")
                text_to_speech(text, speech_output_path)
                speech_file = "output.mp3"

                result = f"Text: {text} | Braille: {braille_text}"
            else:
                result = "No text provided."

    return render_template(
        "index.html",
        result=result,
        braille_img=braille_img_path,
        speech_file=speech_file
    )

def convert_to_wav(input_path, output_path):
    try:
        ffmpeg.input(input_path).output(output_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000').run(overwrite_output=True)
        return True
    except Exception as e:
        print(f"[ERROR] ffmpeg conversion failed: {e}")
        return False

@app.route("/download")
def download_audio():
    path = os.path.join(STATIC_FOLDER, "output.mp3")
    return send_file(path, as_attachment=True)

@app.route("/download_braille")
def download_braille_image():
    path = os.path.join(STATIC_FOLDER, "braille_output.png")
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
