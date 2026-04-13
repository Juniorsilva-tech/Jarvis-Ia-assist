"""
Wake Word v2 — usa vosk (offline, rápido) com fallback para SpeechRecognition.
Muito mais confiável para detecção contínua.
"""
import threading
import time
import os

_running = False
_callback = None
_thread = None


def _loop_vosk():
    """Vosk — reconhecimento offline, sem depender de internet."""
    global _running
    try:
        import vosk
        import sounddevice as sd
        import queue
        import json

        model_path = os.path.join(os.path.dirname(__file__), "..", "models", "vosk-pt")
        if not os.path.exists(model_path):
            print("[Wake Word] Modelo Vosk não encontrado, usando SpeechRecognition.")
            return False

        model = vosk.Model(model_path)
        q = queue.Queue()

        def callback(indata, frames, time, status):
            q.put(bytes(indata))

        with sd.RawInputStream(samplerate=16000, blocksize=8000,
                               dtype="int16", channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, 16000)
            print("[Wake Word Vosk] Ouvindo... diga 'Jarvis [comando]'")
            while _running:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").lower()
                    if "jarvis" in text and _callback:
                        cmd = text.replace("jarvis", "").strip(" ,.")
                        if cmd:
                            _callback(cmd)
        return True
    except Exception as e:
        print(f"[Wake Word] Vosk indisponível ({e}), usando SpeechRecognition.")
        return False


def _loop_sr():
    """Fallback: SpeechRecognition com Google."""
    global _running
    try:
        import speech_recognition as sr
    except ImportError:
        print("[Wake Word] Instale: pip install SpeechRecognition")
        return

    rec = sr.Recognizer()
    rec.pause_threshold = 1.8
    rec.energy_threshold = 300
    rec.dynamic_energy_threshold = True
    print("[Wake Word SR] Ouvindo... diga 'Jarvis [comando]'")

    while _running:
        try:
            with sr.Microphone() as src:
                rec.adjust_for_ambient_noise(src, duration=0.3)
                audio = rec.listen(src, timeout=6, phrase_time_limit=10)
            text = rec.recognize_google(audio, language="pt-BR").lower()
            if "jarvis" in text:
                cmd = text.replace("jarvis", "").strip(" ,.")
                if cmd and _callback:
                    _callback(cmd)
                elif _callback:
                    # Só "Jarvis" — escuta próximo comando
                    with sr.Microphone() as src:
                        rec.adjust_for_ambient_noise(src, duration=0.2)
                        audio2 = rec.listen(src, timeout=7, phrase_time_limit=25)
                    cmd2 = rec.recognize_google(audio2, language="pt-BR")
                    if cmd2 and _callback:
                        _callback(cmd2)
        except Exception:
            pass
        time.sleep(0.05)


def _loop():
    if not _loop_vosk():
        _loop_sr()


def start(callback):
    global _thread, _running, _callback
    if _running:
        return
    _callback = callback
    _running = True
    _thread = threading.Thread(target=_loop, daemon=True)
    _thread.start()


def stop():
    global _running
    _running = False
