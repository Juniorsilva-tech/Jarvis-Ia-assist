"""
Jarvis AI — Entry Point CLI
Para GUI: python interfaces/hud/hud_ultra/app.py
"""

from core.brain.orchestrator import Orchestrator
from core.memory.memory_manager import init_memory


def main():
    print("Jarvis v4 iniciando...")
    init_memory()
    orchestrator = Orchestrator()
    print("Jarvis pronto! Digite 'sair' para encerrar, 'voz' para microfone.\n")

    while True:
        try:
            user_input = input("Voce: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["sair", "exit", "quit"]:
                print("Jarvis encerrado.")
                break
            if user_input.lower() == "voz":
                try:
                    from voice.stt import listen_voice
                    print("Ouvindo...")
                    user_input = listen_voice()
                    if not user_input:
                        print("Nao entendi. Tente novamente.")
                        continue
                    print(f"Voce disse: {user_input}")
                except Exception as e:
                    print(f"Erro no microfone: {e}")
                    continue

            response = orchestrator.run(user_input)
            print(f"Jarvis: {response}\n")

            try:
                from voice.tts import speak
                speak(response)
            except Exception:
                pass

        except KeyboardInterrupt:
            print("\nJarvis encerrado.")
            break
        except Exception as e:
            print(f"Erro: {e}")


if __name__ == "__main__":
    main()
