"""
Routine Learner — aprende hábitos e rotinas do usuário.
"""
import json, os
from datetime import datetime

ROUTINE_FILE = "memory_routine.json"
_data = {}

def _load():
    global _data
    if os.path.exists(ROUTINE_FILE):
        try:
            with open(ROUTINE_FILE, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            _data = {}

def _save():
    try:
        with open(ROUTINE_FILE, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def record_action(action: str):
    _load()
    now = datetime.now()
    hour = now.strftime("%H")
    day  = ["seg","ter","qua","qui","sex","sab","dom"][now.weekday()]
    key  = f"{day}_{hour}"
    if key not in _data:
        _data[key] = []
    _data[key].append(action[:80])
    if len(_data[key]) > 10:
        _data[key].pop(0)
    _save()

def get_suggestions() -> str:
    _load()
    now = datetime.now()
    hour = now.strftime("%H")
    day  = ["seg","ter","qua","qui","sex","sab","dom"][now.weekday()]
    key  = f"{day}_{hour}"
    actions = _data.get(key, [])
    if not actions:
        return ""
    from collections import Counter
    common = Counter(actions).most_common(3)
    return "Você costuma: " + ", ".join(a for a, _ in common)

def get_routine_summary() -> str:
    _load()
    if not _data:
        return "Ainda aprendendo sua rotina..."
    lines = []
    for key, actions in list(_data.items())[-5:]:
        if actions:
            lines.append(f"{key}: {actions[-1]}")
    return "Rotina aprendida:\n" + "\n".join(lines)
