import speech_recognition as sr
from gtts import gTTS

def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("[INFO] Please speak something...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(f"[DEBUG] Recognized speech: {text}")
            return text
        except sr.UnknownValueError:
            print("[WARN] Could not understand audio.")
            return ""
        except sr.RequestError:
            print("[ERROR] Speech recognition service error.")
            return ""

def text_to_speech(text, output_path="static/output.mp3"):
    text = text.strip()
    if not text:
        raise ValueError("Cannot convert empty or whitespace text to speech.")
    tts = gTTS(text)
    tts.save(output_path)
