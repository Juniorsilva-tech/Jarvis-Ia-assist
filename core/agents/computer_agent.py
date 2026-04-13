import pyautogui
import time


class ComputerAgent:

    def run(self, step: dict):

        action = step.get("action")

        if action == "move_mouse":
            x = step.get("x", 500)
            y = step.get("y", 500)
            pyautogui.moveTo(x, y, duration=0.5)
            return f"Mouse movido para {x},{y}"

        if action == "click":
            pyautogui.click()
            return "Clique executado"

        if action == "type":
            text = step.get("text", "")
            pyautogui.write(text, interval=0.05)
            return f"Digitado: {text}"

        if action == "hotkey":
            keys = step.get("keys", [])
            pyautogui.hotkey(*keys)
            return f"Hotkey executada: {keys}"

        return "Ação desconhecida"