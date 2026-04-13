import customtkinter as ctk
import threading
from core.brain.orchestrator import execute_user_request

# cores
COLOR_BG = "#0f172a"
COLOR_PANEL = "#111827"
COLOR_USER = "#2563eb"
COLOR_JARVIS = "#10b981"

COLOR_GREEN = "#22c55e"
COLOR_YELLOW = "#eab308"
COLOR_RED = "#ef4444"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class JarvisHUD(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Jarvis AI")
        self.geometry("900x600")
        self.configure(fg_color=COLOR_BG)

        self._build_ui()

    # --------------------------------
    # UI
    # --------------------------------

    def _build_ui(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main = ctk.CTkFrame(self, fg_color=COLOR_PANEL)
        main.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # chat area
        self.chatbox = ctk.CTkTextbox(
            main,
            wrap="word",
            font=("Consolas", 14)
        )

        self.chatbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.chatbox.configure(state="disabled")

        # input
        self.entry = ctk.CTkEntry(
            main,
            placeholder_text="Digite sua mensagem..."
        )

        self.entry.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.entry.bind("<Return>", self._on_enter)

        # status
        self.status = ctk.CTkLabel(
            main,
            text="● Online",
            text_color=COLOR_GREEN
        )

        self.status.grid(row=2, column=0, pady=(0, 10))

    # --------------------------------
    # CHAT
    # --------------------------------

    def _add_message(self, message, sender):

        self.chatbox.configure(state="normal")

        if sender == "user":
            prefix = "Você: "
        else:
            prefix = "Jarvis: "

        self.chatbox.insert("end", f"{prefix}{message}\n\n")
        self.chatbox.see("end")

        self.chatbox.configure(state="disabled")

    # --------------------------------
    # STATUS
    # --------------------------------

    def _set_status(self, text, color):

        self.status.configure(text=text, text_color=color)

    # --------------------------------
    # EVENTOS
    # --------------------------------

    def _on_enter(self, event=None):

        user_input = self.entry.get().strip()

        if not user_input:
            return

        self.entry.delete(0, "end")

        self._add_message(user_input, "user")

        threading.Thread(
            target=self._process,
            args=(user_input,),
            daemon=True
        ).start()

    # --------------------------------
    # PROCESSAMENTO
    # --------------------------------

    def _process(self, user_input):

        self.after(
            0,
            lambda: self._set_status("● Pensando...", COLOR_YELLOW)
        )

        try:

            result = execute_user_request(user_input)

            if isinstance(result, dict):
                response = result.get("result", "Sem resposta")
            else:
                response = str(result)

            self.after(
                0,
                lambda: self._add_message(response, "jarvis")
            )

        except Exception as e:

            error = str(e)

            self.after(
                0,
                lambda: self._add_message(f"Erro: {error}", "jarvis")
            )

        finally:

            self.after(
                0,
                lambda: self._set_status("● Online", COLOR_GREEN)
            )


# --------------------------------
# MAIN
# --------------------------------

def main():

    app = JarvisHUD()
    app.mainloop()


if __name__ == "__main__":
    main()