import os, sys, webbrowser, subprocess, datetime, threading
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
NAME=os.getenv("ULTRON_NAME","ULTRON")
WAKE=os.getenv("WAKE_WORD","ultron").lower()
API_KEY=os.getenv("GEMINI_API_KEY","")

try:
    import speech_recognition as sr
except ImportError:
    sr=None

def say(text):
    print(f"{NAME}: {text}")
    try:
        import pyttsx3
        e=pyttsx3.init()
        e.say(text)
        e.runAndWait()
    except Exception:
        pass

def ask_ai(prompt):
    if not API_KEY:
        return "Gemini is not configured yet. Put your key in the local .env file."
    try:
        from google import genai
        client=genai.Client(api_key=API_KEY)
        r=client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return getattr(r,"text",None) or "I did not receive a response."
    except Exception as e:
        return f"AI error: {e}"

def handle(cmd):
    c=cmd.lower().strip()
    if not c: return
    if "time" in c:
        say(datetime.datetime.now().strftime("It is %I:%M %p."))
    elif "date" in c:
        say(datetime.datetime.now().strftime("Today is %A, %d %B %Y."))
    elif c.startswith("open "):
        target=c[5:].strip()
        urls={"youtube":"https://youtube.com","google":"https://google.com","github":"https://github.com"}
        if target in urls: webbrowser.open(urls[target]); say(f"Opening {target}.")
        else: webbrowser.open("https://www.google.com/search?q="+target.replace(" ","+")); say("Searching the web.")
    elif "screenshot" in c:
        try:
            import pyautogui
            p=Path.home()/f"Desktop/ultron-{datetime.datetime.now():%Y%m%d-%H%M%S}.png"
            pyautogui.screenshot().save(p); say(f"Screenshot saved to {p}.")
        except Exception as e: say(f"Screenshot failed: {e}")
    elif "calculator" in c:
        subprocess.Popen(["calc.exe"]); say("Opening Calculator.")
    elif c in {"exit","quit","shutdown ultron","stop"}:
        say("Standing by."); raise SystemExit
    else:
        say(ask_ai(cmd))

def listen():
    if sr is None:
        say("SpeechRecognition is not installed.")
        return
    r=sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source,duration=0.5)
        say(f"Online. Say {NAME} followed by a command.")
        while True:
            try:
                audio=r.listen(source,timeout=None,phrase_time_limit=8)
                text=r.recognize_google(audio).lower()
                print("YOU:",text)
                if WAKE in text:
                    command=text.split(WAKE,1)[1].strip()
                    handle(command)
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                say(f"Speech service error: {e}")
            except KeyboardInterrupt:
                break

if __name__=="__main__":
    listen()
