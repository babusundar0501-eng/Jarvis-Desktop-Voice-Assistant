import json, os, subprocess, sys, threading, webbrowser
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QFrame
APP_DIR = Path(__file__).resolve().parent
MEMORY_FILE = APP_DIR / "memory.json"
PHONE_NUMBER = os.getenv("ULTRON_PHONE_NUMBER", "+6581238904")
WAKE_WORD = os.getenv("ULTRON_WAKE_WORD", "ultron")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
try:
    from google import genai
except Exception:
    genai = None
try:
    import pyttsx3
except Exception:
    pyttsx3 = None
try:
    import speech_recognition as sr
except Exception:
    sr = None

class Brain:
    def __init__(self):
        self.client = None
        if GEMINI_KEY and genai:
            try: self.client = genai.Client(api_key=GEMINI_KEY)
            except Exception: self.client = None
    def ask(self, text):
        if not self.client:
            return "Gemini is not configured. Put your API key in ULTRON/.env and restart."
        try:
            response = self.client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=("You are ULTRON, a Windows desktop voice assistant. Be concise and useful. "
                          "You control only the PC and phone-link actions exposed by this app. "
                          "Do not claim to control smart-home devices. User request: " + text)
            )
            return getattr(response, "text", None) or "I could not generate a response."
        except Exception as e:
            return f"AI error: {e}"

class Memory:
    def __init__(self):
        try: self.data = json.loads(MEMORY_FILE.read_text(encoding="utf-8")) if MEMORY_FILE.exists() else {}
        except Exception: self.data = {}
    def save(self):
        MEMORY_FILE.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
    def remember(self, key, value):
        self.data[key] = value
        self.save()

class VoiceWorker(QThread):
    heard = Signal(str)
    status = Signal(str)
    def run(self):
        if not sr:
            self.status.emit("SpeechRecognition is not installed."); return
        recognizer = sr.Recognizer()
        try: mic = sr.Microphone()
        except Exception as e:
            self.status.emit(f"Microphone unavailable: {e}"); return
        self.status.emit("Listening for 'Ultron'...")
        while not self.isInterruptionRequested():
            try:
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=7)
                text = recognizer.recognize_google(audio).strip()
                if WAKE_WORD.lower() in text.lower():
                    command = text.lower().split(WAKE_WORD.lower(), 1)[1].strip(" ,.!?")
                    self.heard.emit(command or "Hello Ultron")
            except sr.WaitTimeoutError:
                continue
            except Exception:
                continue

class Speaker:
    def __init__(self):
        self.engine = None
        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 175)
            except Exception: self.engine = None
    def say(self, text):
        if not self.engine: return
        def work():
            try:
                self.engine.say(text); self.engine.runAndWait()
            except Exception: pass
        threading.Thread(target=work, daemon=True).start()

def open_target(target):
    if target.startswith(("http://", "https://")): webbrowser.open(target)
    else: subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)

def phone_action(kind):
    uri = f"tel:{PHONE_NUMBER}" if kind == "call" else f"sms:{PHONE_NUMBER}"
    try:
        webbrowser.open(uri)
        return f"Opening {kind} for {PHONE_NUMBER}."
    except Exception as e:
        return f"Could not open phone action: {e}"

class Ultron(QWidget):
    def __init__(self):
        super().__init__()
        self.brain, self.memory, self.speaker = Brain(), Memory(), Speaker()
        self.voice = None
        self.setWindowTitle("ULTRON")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)
        self.build_ui(); self.apply_style()
        self.add_message("SYSTEM", "ULTRON online. Say 'Ultron' or type a command.")
        self.clock = QTimer(self); self.clock.timeout.connect(self.update_clock); self.clock.start(1000)
        self.update_clock()
    def build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(28,24,28,24); root.setSpacing(14)
        top = QHBoxLayout()
        title = QLabel("ULTRON"); title.setObjectName("title"); top.addWidget(title); top.addStretch()
        self.status = QLabel("OFFLINE"); self.status.setObjectName("status"); top.addWidget(self.status)
        self.clock_label = QLabel(); self.clock_label.setObjectName("clock"); top.addWidget(self.clock_label)
        root.addLayout(top)
        line = QFrame(); line.setFrameShape(QFrame.HLine); line.setObjectName("line"); root.addWidget(line)
        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setObjectName("log"); root.addWidget(self.log,1)
        command = QHBoxLayout()
        self.input = QLineEdit(); self.input.setPlaceholderText("Type a command for ULTRON..."); self.input.returnPressed.connect(self.submit); command.addWidget(self.input,1)
        send = QPushButton("EXECUTE"); send.clicked.connect(self.submit); command.addWidget(send)
        self.voice_button = QPushButton("START VOICE"); self.voice_button.clicked.connect(self.toggle_voice); command.addWidget(self.voice_button)
        root.addLayout(command)
        quick = QHBoxLayout()
        for label, cmd in [("WEB SEARCH","search the web for "),("PHONE","call my phone"),("SMS","text my phone"),("TIME","what time is it"),("MEMORY","what do you remember")]:
            b=QPushButton(label); b.clicked.connect(lambda checked=False,c=cmd:self.quick(c)); quick.addWidget(b)
        root.addLayout(quick)
        footer=QLabel(f"Phone identity: {PHONE_NUMBER}   |   No hand tracking   |   No smart-device control"); footer.setObjectName("footer"); root.addWidget(footer)
    def apply_style(self):
        self.setStyleSheet("""
            QWidget { background:#050507; color:#eeeeee; font-family:Segoe UI; }
            QLabel#title { color:#ff3030; font-size:42px; font-weight:800; letter-spacing:7px; }
            QLabel#status { color:#ff3030; font-weight:700; padding:7px 12px; border:1px solid #7b1111; border-radius:6px; }
            QLabel#clock { color:#888888; font-size:14px; margin-left:10px; }
            QTextEdit#log { background:#09090c; border:1px solid #3a1010; border-radius:10px; padding:18px; font-size:15px; }
            QLineEdit { background:#0b0b0f; border:1px solid #481111; border-radius:8px; padding:14px; color:#fff; font-size:15px; }
            QPushButton { background:#120b0b; border:1px solid #6e1717; border-radius:7px; padding:12px 15px; color:#fff; font-weight:700; }
            QPushButton:hover { background:#271010; border-color:#d52a2a; }
            QLabel#footer { color:#666; font-size:12px; padding-top:5px; }
        """)
    def update_clock(self): self.clock_label.setText(datetime.now().strftime("%H:%M:%S"))
    def add_message(self, who, text): self.log.append(f"<b style='color:#ff3030'>{who}</b>  {text}")
    def quick(self, command): self.input.setText(command); self.submit()
    def submit(self):
        text=self.input.text().strip(); self.input.clear()
        if text: self.process(text)
    def process(self, text):
        self.add_message("YOU", text); lower=text.lower()
        if lower in ("hello ultron","hello"): answer="At your service."
        elif "what time" in lower or lower=="time": answer=datetime.now().strftime("It is %I:%M %p.")
        elif "my phone" in lower and "call" in lower: answer=phone_action("call")
        elif "text my phone" in lower or "sms my phone" in lower: answer=phone_action("sms")
        elif lower.startswith("open "):
            target=text[5:].strip(); sites={"youtube":"https://youtube.com","google":"https://google.com","github":"https://github.com"}
            open_target(sites.get(target.lower(),target)); answer=f"Opening {target}."
        elif lower.startswith("search the web for "):
            q=text[len("search the web for "):].strip(); webbrowser.open("https://www.google.com/search?q="+q.replace(" ","+")); answer=f"Searching the web for {q}."
        elif lower.startswith("remember "):
            payload=text[len("remember "):]
            if " is " in payload:
                key,value=payload.split(" is ",1); self.memory.remember(key.strip(),value.strip()); answer="I will remember that."
            else: answer="Use: remember NAME is VALUE."
        elif "what do you remember" in lower: answer=json.dumps(self.memory.data,ensure_ascii=False) if self.memory.data else "My memory is empty."
        elif lower in ("exit","quit","shutdown ultron"): self.close(); return
        else: answer=self.brain.ask(text)
        self.add_message("ULTRON",answer); self.speaker.say(answer)
    def toggle_voice(self):
        if self.voice and self.voice.isRunning():
            self.voice.requestInterruption(); self.voice.wait(1500); self.voice=None
            self.voice_button.setText("START VOICE"); self.status.setText("OFFLINE"); self.add_message("SYSTEM","Voice mode stopped."); return
        self.voice=VoiceWorker(); self.voice.heard.connect(self.process); self.voice.status.connect(lambda s:self.status.setText("LISTENING" if "Listening" in s else "VOICE ERROR"))
        self.voice.start(); self.voice_button.setText("STOP VOICE"); self.status.setText("LISTENING")
        self.add_message("SYSTEM","Voice mode active. Say 'Ultron' followed by a command.")

if __name__=="__main__":
    app=QApplication(sys.argv); app.setApplicationName("ULTRON"); window=Ultron(); window.show(); sys.exit(app.exec())
