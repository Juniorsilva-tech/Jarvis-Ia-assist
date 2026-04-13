"""
TTS - Text to Speech
Engine persistente, thread-safe, sem reinicialização a cada fala.
"""

import pyttsx3
import threading

_engine = None
_lock = threading.Lock()
_initialized = False


def _init_engine():
    global _engine, _initialized
    if _initialized:
        return _engine
    try:
        _engine = pyttsx3.init()
        voices = _engine.getProperty('voices')
        # Prefere voz portuguesa
        for v in voices:
            name = v.name.lower()
            if 'brazil' in name or 'portuguese' in name or 'maria' in name or 'luciana' in name:
                _engine.setProperty('voice', v.id)
                break
        _engine.setProperty('rate', 160)
        _engine.setProperty('volume', 1.0)
        _initialized = True
    except Exception as e:
        print(f"⚠️  TTS indisponível: {e}")
        _engine = None
        _initialized = True
    return _engine


def speak(text: str):
    """Fala o texto. Engine é reutilizada — não reinicializa a cada chamada."""
    if not text or not text.strip():
        return

    with _lock:
        engine = _init_engine()
        if not engine:
            return
        try:
            # Para qualquer fala anterior antes de começar nova
            try:
                engine.stop()
            except Exception:
                pass
            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            # Engine foi destruída — reinicializa
            global _initialized
            _initialized = False
            _engine_new = _init_engine()
            if _engine_new:
                try:
                    _engine_new.say(text)
                    _engine_new.runAndWait()
                except Exception:
                    pass
        except Exception as e:
            print(f"⚠️  Erro TTS: {e}")


def stop_speaking():
    """Para a fala atual imediatamente."""
    with _lock:
        if _engine:
            try:
                _engine.stop()
            except Exception:
                pass
