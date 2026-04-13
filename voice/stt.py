"""
STT - Speech to Text
Escuta até o usuário terminar de falar de verdade.
Sem cortar a fala no meio — silence threshold generoso.
"""

import speech_recognition as sr

recognizer = sr.Recognizer()

# Configurações para não cortar a fala
recognizer.pause_threshold = 2.0        # 2s de silêncio para considerar fim da fala
recognizer.phrase_threshold = 0.3       # sensibilidade para início da fala
recognizer.non_speaking_duration = 1.5  # tempo de silêncio antes de parar de gravar
recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 300


def listen_voice(timeout: int = 15, phrase_limit: int = 60) -> str:
    """
    Escuta até o usuário terminar de falar.
    - timeout: tempo máximo esperando início da fala
    - phrase_limit: tempo máximo de gravação contínua (60s)
    Não corta no meio da frase — aguarda 2s de silêncio real.
    """
    try:
        with sr.Microphone() as source:
            # Calibração rápida de ruído ambiente
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_limit
            )

        text = recognizer.recognize_google(audio, language="pt-BR")
        return text.strip()

    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"❌ Serviço de reconhecimento indisponível: {e}")
        return ""
    except Exception as e:
        print(f"❌ Erro no STT: {e}")
        return ""


# Alias compatível com main.py
listen = listen_voice
