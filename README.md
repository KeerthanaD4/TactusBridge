# 🧠 TactusBridge

TactusBridge is an inclusive web application designed to bridge the communication gap between speech, text, and Braille. It supports seamless bidirectional conversion between these modes, enabling visually impaired individuals and accessibility advocates to interact, learn, and communicate effectively. Currently, the application supports *text-to-braille*, *text-to-speech* and *text-to-braille image* conversion. Image and Speech support is under development.

## 🌐 Features
🔁 **Multi-Mode Bidirectional Conversion:**
- 📝 Text → 🟠 Braille Image + 🔊 Speech
- 🟠 Braille Image → 📝 Text + 🔊 Speech
- 🎤 Speech (live mic or uploaded file) → 🟠 Braille Image + 📝 Text

🧠 **Key Capabilities:**
- Braille rendering using precise 6-dot encoding
- Braille image recognition using OpenCV + clustering
- Text-to-speech with gTTS
- Speech-to-text via microphone and uploaded audio
- Multi-line Braille image generation
- Audio conversion (WebM → WAV) using ffmpeg

## ✅ Current Functionalities
✔️ **Text ↔ Braille Image**  
✔️ **Text ↔ Speech**  
✔️ **Text ↔ Braille Language (dot pattern representation)**  

🚧 **In Progress**:
- 🖼️ Braille Image ➜ Text/Speech
- 🎤 Speech ➜ Text/Braille


## 🧰 Technologies Used
- **Flask** – Web framework
- **OpenCV + Pillow** – Braille image generation and preprocessing
- **gTTS** – Text-to-speech
- **SpeechRecognition** – For upcoming speech-to-text feature
- **HTML/CSS + JS** – Web UI
- **Python** – Core logic and utilities

## 🔁 Supported Conversions (Now)

| From       | To               | Status       |
|------------|------------------|--------------|
| Text       | Braille Image     | ✅ Completed |
| Text       | Speech            | ✅ Completed |
| Text       | Braille Language  | ✅ Completed |
| Braille Image | Text/Speech     | 🚧 In Progress |
| Speech     | Text/Braille      | 🚧 In Progress |


## ⚙️ Setup Instructions
1️⃣ **Clone the Repository**
```sh
git clone https://github.com/your-username/TactusBridge.git
cd TactusBridge
```
2️⃣ **Install dependencies**
```sh
pip install flask pillow opencv-python numpy gTTS speechrecognition ffmpeg-python
```
3️⃣ **Run the Flask app! 🚀**
```sh
python app.py
```
