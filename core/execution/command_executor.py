"""
Command Executor - Jarvis
Executor de baixo nível para comandos do sistema.
"""

import os
import subprocess


class CommandExecutor:
    def execute(self, action_data: dict) -> str:
        action = action_data.get("action")
        try:
            if action == "open_app":
                return self.open_app(action_data.get("target", ""))
            elif action == "create_file":
                return self.create_file(action_data)
            elif action == "run_code":
                return self.run_code(action_data.get("code", ""))
            return f"Ação não reconhecida: {action}"
        except Exception as e:
            return f"Erro ao executar '{action}': {e}"

    def open_app(self, app_name: str) -> str:
        if not app_name:
            return "❌ Nome do aplicativo não especificado"
        try:
            subprocess.Popen(app_name, shell=True)
            return f"✅ {app_name} aberto com sucesso"
        except Exception as e:
            return f"❌ Erro ao abrir {app_name}: {e}"

    def create_file(self, data: dict) -> str:
        filename = data.get("filename", "arquivo.txt")
        content = data.get("content", "")

        # Garante encoding UTF-8 no header de arquivos Python
        if filename.endswith(".py") and not content.startswith("# -*- coding"):
            content = "# -*- coding: utf-8 -*-\n" + content

        try:
            os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ Arquivo {filename} criado"
        except Exception as e:
            return f"❌ Erro ao criar {filename}: {e}"

    def run_code(self, code: str) -> str:
        if not code.strip():
            return "❌ Código vazio"
        filename = "temp_code.py"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)
            result = subprocess.run(
                ["python", filename], capture_output=True, text=True, timeout=15
            )
            output = result.stdout or result.stderr or "(sem saída)"
            return f"▶️ Saída:\n{output[:500]}"
        except subprocess.TimeoutExpired:
            return "⚠️ Timeout — código demorou mais de 15 segundos"
        except Exception as e:
            return f"❌ Erro ao executar código: {e}"
