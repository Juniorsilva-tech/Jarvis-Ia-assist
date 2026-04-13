"""
PC Controller - Jarvis
Controle total do PC: arquivos, processos, volume, screenshot, teclado, mouse.
Pastas críticas são protegidas e nunca podem ser modificadas.
"""

import os
import sys
import subprocess
import shutil
import psutil
import time
from datetime import datetime
from pathlib import Path

# ── Pastas protegidas — Jarvis NUNCA toca aqui ────────────────────────────────
PROTECTED_PATHS = [
    "C:\\Windows",
    "C:\\Windows\\System32",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    os.path.expanduser("~\\AppData\\Roaming\\Microsoft"),
    os.path.expanduser("~\\AppData\\Local\\Microsoft"),
]


def is_protected(path: str) -> bool:
    """Retorna True se o caminho é uma pasta crítica do sistema."""
    path_obj = Path(path).resolve()
    for protected in PROTECTED_PATHS:
        try:
            protected_obj = Path(protected).resolve()
            if path_obj == protected_obj or protected_obj in path_obj.parents:
                return True
        except Exception:
            pass
    return False


# ── Arquivos e Pastas ─────────────────────────────────────────────────────────

def list_files(path: str = ".") -> str:
    """Lista arquivos de uma pasta."""
    try:
        p = Path(path).expanduser()
        if not p.exists():
            return f"❌ Pasta não encontrada: {path}"
        items = list(p.iterdir())
        dirs  = [f"📁 {i.name}" for i in items if i.is_dir()]
        files = [f"📄 {i.name} ({_size(i)})" for i in items if i.is_file()]
        result = dirs + files
        return f"📂 {path}:\n" + "\n".join(result[:30]) if result else "Pasta vazia."
    except Exception as e:
        return f"❌ Erro: {e}"


def _size(path: Path) -> str:
    try:
        s = path.stat().st_size
        if s < 1024: return f"{s}B"
        if s < 1024**2: return f"{s//1024}KB"
        return f"{s//1024**2}MB"
    except Exception:
        return "?"


def create_folder(path: str) -> str:
    if is_protected(path):
        return "🔒 Pasta protegida — Jarvis não pode modificar pastas do sistema."
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return f"✅ Pasta criada: {path}"
    except Exception as e:
        return f"❌ Erro ao criar pasta: {e}"


def delete_file(path: str) -> str:
    if is_protected(path):
        return "🔒 Pasta protegida — operação bloqueada por segurança."
    try:
        p = Path(path)
        if not p.exists():
            return f"❌ Não encontrado: {path}"
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return f"✅ Removido: {path}"
    except Exception as e:
        return f"❌ Erro: {e}"


def move_file(src: str, dst: str) -> str:
    if is_protected(src) or is_protected(dst):
        return "🔒 Operação bloqueada — caminho protegido."
    try:
        shutil.move(src, dst)
        return f"✅ Movido: {src} → {dst}"
    except Exception as e:
        return f"❌ Erro: {e}"


def copy_file(src: str, dst: str) -> str:
    if is_protected(dst):
        return "🔒 Destino protegido."
    try:
        if Path(src).is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return f"✅ Copiado: {src} → {dst}"
    except Exception as e:
        return f"❌ Erro: {e}"


def read_file(path: str, max_chars: int = 2000) -> str:
    """Lê conteúdo de um arquivo de texto."""
    if is_protected(path):
        return "🔒 Arquivo protegido."
    try:
        content = Path(path).read_text(encoding="utf-8", errors="ignore")
        if len(content) > max_chars:
            return content[:max_chars] + f"\n...[truncado — {len(content)} chars total]"
        return content
    except Exception as e:
        return f"❌ Erro ao ler: {e}"


def write_file(path: str, content: str) -> str:
    if is_protected(path):
        return "🔒 Caminho protegido."
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"✅ Arquivo salvo: {path}"
    except Exception as e:
        return f"❌ Erro: {e}"


# ── Processos ─────────────────────────────────────────────────────────────────

def list_processes(filter_name: str = "") -> str:
    """Lista processos rodando."""
    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                name = p.info['name'] or ""
                if filter_name and filter_name.lower() not in name.lower():
                    continue
                mem = p.info['memory_info'].rss // 1024 // 1024 if p.info['memory_info'] else 0
                procs.append(f"PID {p.info['pid']:6} | {name[:30]:30} | {mem}MB RAM")
            except Exception:
                pass
        if not procs:
            return "Nenhum processo encontrado."
        return "⚙ Processos:\n" + "\n".join(procs[:20])
    except Exception as e:
        return f"❌ Erro: {e}"


def kill_process(name_or_pid: str) -> str:
    """Mata um processo pelo nome ou PID."""
    killed = []
    try:
        pid = int(name_or_pid)
        psutil.Process(pid).terminate()
        return f"✅ Processo {pid} encerrado."
    except ValueError:
        pass
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if name_or_pid.lower() in (p.info['name'] or "").lower():
                p.terminate()
                killed.append(p.info['name'])
        except Exception:
            pass
    return f"✅ Encerrados: {', '.join(killed)}" if killed else f"❌ Processo não encontrado: {name_or_pid}"


def get_system_info() -> str:
    """Informações do sistema em tempo real."""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        now = datetime.now()
        return (
            f"🖥️  Sistema — {now.strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"CPU: {cpu}%\n"
            f"RAM: {ram.used//1024//1024}MB / {ram.total//1024//1024}MB ({ram.percent}%)\n"
            f"Disco: {disk.used//1024//1024//1024}GB / {disk.total//1024//1024//1024}GB ({disk.percent}%)"
        )
    except Exception as e:
        return f"❌ Erro: {e}"


# ── Volume e Mídia ────────────────────────────────────────────────────────────

def set_volume(level: int) -> str:
    """Define volume do sistema (0-100). Apenas Windows."""
    level = max(0, min(100, level))
    try:
        # Windows: usa nircmd ou PowerShell
        script = f"(New-Object -ComObject WScript.Shell).SendKeys([char]174)"
        # Método mais simples via PowerShell
        cmd = f'powershell -c "& {{Add-Type -TypeDefinition \'using System.Runtime.InteropServices; public class Audio {{[DllImport(\\\"winmm.dll\\\")]}}\'}}"'
        # Usa pycaw se disponível
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            import ctypes
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(level / 100, None)
            return f"🔊 Volume: {level}%"
        except ImportError:
            # Fallback: nircmd
            os.system(f"nircmd.exe setsysvolume {int(level * 655.35)}")
            return f"🔊 Volume: {level}%"
    except Exception as e:
        return f"❌ Erro ao ajustar volume: {e}"


def take_screenshot(filename: str = "") -> str:
    """Tira screenshot da tela."""
    try:
        import PIL.ImageGrab as ImageGrab
        if not filename:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        folder = Path.home() / "Pictures" / "Jarvis"
        folder.mkdir(parents=True, exist_ok=True)
        filepath = folder / filename
        img = ImageGrab.grab()
        img.save(str(filepath))
        return f"📸 Screenshot salvo: {filepath}"
    except ImportError:
        return "❌ Instale Pillow: pip install Pillow"
    except Exception as e:
        return f"❌ Erro: {e}"


# ── Hora e Data ───────────────────────────────────────────────────────────────

def get_time() -> str:
    now = datetime.now()
    hora = now.hour
    if hora < 12:
        periodo = "manhã"
    elif hora < 18:
        periodo = "tarde"
    else:
        periodo = "noite"
    return (
        f"🕐 Agora são {now.strftime('%H:%M')} da {periodo}.\n"
        f"📅 {now.strftime('%A, %d de %B de %Y')}."
    )


# ── Spotify ───────────────────────────────────────────────────────────────────

def control_spotify(action: str, query: str = "") -> str:
    """
    Controla Spotify via teclas de mídia ou URI.
    action: play, pause, next, prev, search
    """
    try:
        import pyautogui

        actions_keys = {
            "pause": "playpause",
            "play":  "playpause",
            "next":  "nexttrack",
            "prev":  "prevtrack",
            "anterior": "prevtrack",
            "proxima":  "nexttrack",
        }

        if action in actions_keys:
            pyautogui.press(actions_keys[action])
            return f"🎵 Spotify: {action}"

        if action == "search" and query:
            # Abre Spotify e pesquisa
            subprocess.Popen(["start", "spotify:search:" + query], shell=True)
            return f"🎵 Pesquisando no Spotify: {query}"

        if action == "open":
            os.system("start spotify")
            return "🎵 Abrindo Spotify..."

    except ImportError:
        return "❌ Instale pyautogui: pip install pyautogui"
    except Exception as e:
        return f"❌ Erro Spotify: {e}"

    return f"❌ Ação Spotify não reconhecida: {action}"
