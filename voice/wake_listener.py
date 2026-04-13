import queue
import sounddevice as sd
import vosk
import json

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def listen_for_wake_word():
    model = vosk.Model("model")
    recognizer = vosk.KaldiRecognizer(model, 16000)

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype='int16',
        channels=1,
        callback=callback
    ):
        print("🟢 Aguardando 'jarvis'...")

        while True:
            data = q.get()

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")

                if "jarvis" in text.lower():
                    print("🔥 Wake word detectada!")
                    return True