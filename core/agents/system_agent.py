"""
SystemAgent v5 — fix Spotify Microsoft Store + comandos mais precisos.
"""
import os
import subprocess
import webbrowser


class SystemAgent:
    name = "system"

    # Apps mapeados com comandos específicos para Windows
    APP_MAP = {
        "spotify":    ["spotify", "shell:AppsFolder\\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify"],
        "chrome":     ["chrome", "start chrome"],
        "edge":       ["edge", "start msedge"],
        "firefox":    ["firefox", "start firefox"],
        "notepad":    ["notepad", "notepad"],
        "calculadora":["calc", "calc"],
        "calc":       ["calc", "calc"],
        "explorer":   ["explorer", "explorer"],
        "word":       ["winword", "start winword"],
        "excel":      ["excel", "start excel"],
        "vscode":     ["code", "code ."],
        "terminal":   ["cmd", "start cmd"],
        "powershell": ["powershell", "start powershell"],
        "discord":    ["discord", "start discord"],
        "whatsapp":   ["whatsapp", "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!WhatsAppDesktop"],
        "telegram":   ["telegram", "start telegram"],
        "vlc":        ["vlc", "start vlc"],
        "steam":      ["steam", "start steam"],
        "obs":        ["obs64", "start obs64"],
    }

    def execute(self, steps: list, raw_input: str = "") -> str:
        results = []
        for step in steps:
            results.append(self._handle(step.get("action", ""), step, raw_input))
        return "\n".join(r for r in results if r)

    def run(self, step: dict) -> dict:
        return {"agent": "system", "result": self.execute([step])}

    def _handle(self, action: str, step: dict, raw: str = "") -> str:
        if action == "open_app":
            return self._open_app(step.get("target", raw))
        elif action in ("execute_command", "run_command"):
            return self._run_cmd(step.get("command", raw))
        elif action == "get_time":
            return self._time()
        elif action == "screenshot":
            return self._screenshot()
        elif action == "system_info":
            return self._sysinfo()
        elif action == "set_volume":
            return self._volume(int(step.get("level", 50)))
        elif action == "spotify":
            return self._spotify(step.get("spotify_action", "open"), step.get("query", ""))
        elif action == "kill_process":
            return self._kill(step.get("target", raw))
        elif action == "list_files":
            return self._list(step.get("path", "."))
        elif action == "search_web":
            q = step.get("query", raw)
            webbrowser.open(f"https://www.google.com/search?q={q}")
            return f"Pesquisando: {q}"
        elif action == "open_file":
            path = step.get("path", "")
            try:
                os.startfile(path)
                return f"Abrindo: {path}"
            except Exception as e:
                return f"Erro: {e}"
        elif action == "create_folder":
            path = step.get("path", "")
            try:
                os.makedirs(path, exist_ok=True)
                return f"Pasta criada: {path}"
            except Exception as e:
                return f"Erro: {e}"
        else:
            if raw:
                return self._run_cmd(raw)
            return f"Ação não reconhecida: {action}"

    def _open_app(self, target: str) -> str:
        t = target.lower().strip()
        for key, (process, cmd) in self.APP_MAP.items():
            if key in t:
                if key == "spotify":
                    return self._spotify("open", "")
                try:
                    subprocess.Popen(cmd, shell=True)
                    return f"Abrindo {key}."
                except Exception:
                    os.system(cmd)
                    return f"Abrindo {key}."
        # Tenta abrir diretamente
        os.system(f"start {target}")
        return f"Tentando abrir: {target}"

    def _spotify(self, action: str = "open", query: str = "") -> str:
        """Abre o Spotify instalado pela Microsoft Store corretamente."""
        # URI do Spotify na Microsoft Store
        spotify_uri = "shell:AppsFolder\\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify"

        if action in ("open", "play") and not query:
            try:
                subprocess.Popen(["explorer.exe", spotify_uri])
                return "Spotify aberto."
            except Exception:
                # Fallback: tenta pelo nome do executável
                os.system("start spotify")
                return "Spotify aberto."

        if query:
            # Abre Spotify e busca a música/playlist
            try:
                # Abre pelo URI de busca do Spotify
                search = query.replace(" ", "%20")
                os.system(f"start spotify:search:{search}")
                return f"Spotify: buscando '{query}'"
            except Exception:
                subprocess.Popen(["explorer.exe", spotify_uri])
                return f"Spotify aberto. Busque por: {query}"

        # Controle via teclas de mídia
        try:
            import pyautogui
            key_map = {
                "pause": "playpause", "play": "playpause",
                "next": "nexttrack", "proxima": "nexttrack",
                "prev": "prevtrack", "anterior": "prevtrack",
            }
            if action in key_map:
                pyautogui.press(key_map[action])
                return f"Spotify: {action}"
        except ImportError:
            pass

        return "Spotify: comando enviado."

    def _run_cmd(self, cmd: str) -> str:
        if not cmd or not cmd.strip():
            return "Comando vazio."
        blocked = ["format c:", "del /f /s /q c:\\", "rmdir /s /q c:\\windows"]
        if any(b in cmd.lower() for b in blocked):
            return "Comando bloqueado por segurança."
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True,
                               text=True, timeout=15, encoding="utf-8", errors="ignore")
            out = r.stdout.strip() or r.stderr.strip()
            return out[:500] if out else "Executado."
        except subprocess.TimeoutExpired:
            return "Timeout."
        except Exception as e:
            return f"Erro: {e}"

    def _time(self) -> str:
        from datetime import datetime
        n = datetime.now()
        dias = ["segunda","terça","quarta","quinta","sexta","sábado","domingo"]
        return f"São {n.strftime('%H:%M')} de {dias[n.weekday()]}, {n.strftime('%d/%m/%Y')}."

    def _screenshot(self) -> str:
        try:
            import pyautogui
            pasta = os.path.join(os.path.expanduser("~"), "Pictures")
            os.makedirs(pasta, exist_ok=True)
            from datetime import datetime
            path = os.path.join(pasta, f"jarvis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            pyautogui.screenshot().save(path)
            return f"Screenshot: {path}"
        except ImportError:
            return "Instale: pip install pyautogui Pillow"
        except Exception as e:
            return f"Erro: {e}"

    def _sysinfo(self) -> str:
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            return f"CPU: {cpu}% | RAM: {mem.percent}% ({mem.available//1024//1024}MB livre)"
        except ImportError:
            return "Instale: pip install psutil"
        except Exception as e:
            return f"Erro: {e}"

    def _volume(self, level: int) -> str:
        level = max(0, min(100, level))
        try:
            # PowerShell nativo — mais confiável
            script = f"""
$wshShell = New-Object -ComObject WScript.Shell
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
public class Volume {{
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);
    public static void SetVolume(int percent) {{
        for(int i=0;i<50;i++) keybd_event(0xAE,0,0,0);
        int steps = (int)(percent / 2.0);
        for(int i=0;i<steps;i++) keybd_event(0xAF,0,0,0);
    }}
}}
'@
[Volume]::SetVolume({level})
"""
            subprocess.run(["powershell", "-Command", script],
                           capture_output=True, timeout=5)
            return f"Volume: {level}%"
        except Exception:
            try:
                import pyautogui
                for _ in range(50): pyautogui.press("volumedown")
                for _ in range(int(level/2)): pyautogui.press("volumeup")
                return f"Volume: {level}%"
            except Exception as e:
                return f"Erro volume: {e}"

    def _kill(self, name: str) -> str:
        try:
            import psutil
            killed = []
            for p in psutil.process_iter(['name']):
                if name.lower() in p.info['name'].lower():
                    p.kill()
                    killed.append(p.info['name'])
            return f"Encerrado: {', '.join(killed)}" if killed else f"'{name}' não encontrado."
        except ImportError:
            r = subprocess.run(f"taskkill /f /im {name}.exe",
                               shell=True, capture_output=True, text=True)
            return r.stdout.strip() or r.stderr.strip() or f"Encerrado: {name}"
        except Exception as e:
            return f"Erro: {e}"

    def _list(self, path: str) -> str:
        try:
            items = os.listdir(path)
            dirs  = [f"📁 {i}" for i in items if os.path.isdir(os.path.join(path, i))]
            files = [f"📄 {i}" for i in items if os.path.isfile(os.path.join(path, i))]
            return f"{path}:\n" + "\n".join((dirs+files)[:25])
        except Exception as e:
            return f"Erro: {e}"
