# =====================================================
# core/executor.py
# AYZN Main Execution Pipeline
# Gemma + Hierarchical Memory + Step Skills
# Rechecked / Clean Stable Version
# =====================================================

import pyautogui
import time
import json
import subprocess

from ai.models import ask_gemma, ask_intent
from memory.manager import get_memory, save_memory
from memory.skills import auto_learn_from_steps


ACTION_DELAY = 0.15


# =====================================================
# ACTIVE APP DETECTION
# =====================================================

def get_active_app():
    try:
        script = """
        tell application "System Events"
            get name of first application process whose frontmost is true
        end tell
        """

        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True
        )

        return result.stdout.strip().lower()

    except:
        return ""


# =====================================================
# OPEN APP
# =====================================================

def open_app(app_name):
    try:
        subprocess.Popen(["open", "-a", app_name])
        print(f"Opened {app_name}.app ⚡")
        return True

    except:
        print(f"{app_name} not found ❌")
        return False


# =====================================================
# WAIT FOR APP FOCUS
# =====================================================

def wait_for_focus(app_name, timeout=5):
    start = time.time()

    while time.time() - start < timeout:
        active = get_active_app()

        if app_name.lower() in active:
            print(f"[FOCUSED] {active}")
            return True

        time.sleep(0.3)

    print("[FOCUS TIMEOUT]")
    return False


# =====================================================
# EXTRACT JSON STEPS
# =====================================================

def extract_steps(text):
    try:
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            return []

        raw = text[start:end + 1]
        data = json.loads(raw)

        return data.get("steps", [])

    except Exception as e:
        print("[JSON ERROR]", e)
        return []


# =====================================================
# CLEAN / FIX STEPS
# =====================================================

def clean_steps(steps):
    cleaned = []

    for step in steps:
        action = str(step.get("action", "")).strip().lower()
        value = str(step.get("value", "")).strip().lower()

        if not action:
            continue

        # convert cmd -> command
        value = value.replace("cmd", "command")

        # wrong combo sent as key
        if action == "press_key" and "+" in value:
            action = "hotkey"

        # wrong single key sent as hotkey
        if action == "hotkey" and "+" not in value:
            action = "press_key"

        # wait safety cap
        if action == "wait":
            try:
                wait_time = float(value)
                wait_time = min(wait_time, 3)
                value = str(wait_time)
            except:
                value = "1"

        # remove empty values where needed
        if action in ["open_app", "press_key", "hotkey", "type"] and not value:
            continue

        cleaned.append({
            "action": action,
            "value": value
        })

    return cleaned


# =====================================================
# EXECUTE ONE STEP
# =====================================================

def run_step(step):
    action = step["action"]
    value = step["value"]

    print("[STEP]", step)

    try:
        if action == "open_app":
            if open_app(value):
                wait_for_focus(value)
                time.sleep(0.8)

        elif action == "press_key":
            pyautogui.press(value)

        elif action == "hotkey":
            keys = value.split("+")
            pyautogui.hotkey(*keys)

        elif action == "type":
            pyautogui.write(value, interval=0.04)

        elif action == "wait":
            time.sleep(float(value))

    except Exception as e:
        print("[STEP ERROR]", e)


# =====================================================
# EXECUTE STEPS
# =====================================================

def execute_steps(steps):
    print("\n[EXECUTION START]")

    for step in steps:
        run_step(step)
        time.sleep(ACTION_DELAY)

    print("[EXECUTION END]\n")


# =====================================================
# MAIN EXECUTION ENTRY
# =====================================================

def smart_execute(command):
    command = command.strip()

    if not command:
        return False

    print("Checking memory...")

    # -------------------------------------------------
    # LEVEL 1/2/3 MEMORY
    # -------------------------------------------------

    steps = get_memory(command)

    if steps:
        print("Memory hit ⚡")
        execute_steps(steps)
        return True

    # -------------------------------------------------
    # INTENT CLASSIFIER
    # -------------------------------------------------

    meta = ask_intent(command)

    intent = meta.get("intent", "general_task")
    category = meta.get("category", "general")

    print(f"[INTENT] {intent}")
    print(f"[CATEGORY] {category}")

    # -------------------------------------------------
    # GEMMA PLANNER
    # -------------------------------------------------

    print("Trying Gemma ⚡")

    response = ask_gemma(command)

    print(response)

    steps = extract_steps(response)

    if not steps:
        print("[FAILED] No valid steps")
        return False

    # -------------------------------------------------
    # CLEAN PLAN
    # -------------------------------------------------

    steps = clean_steps(steps)

    if not steps:
        print("[FAILED] Invalid cleaned steps")
        return False

    # -------------------------------------------------
    # EXECUTE
    # -------------------------------------------------

    execute_steps(steps)

    # -------------------------------------------------
    # LEARN SUCCESSFUL TASK
    # -------------------------------------------------

    save_memory(command, steps)
    auto_learn_from_steps(steps)

    print(f"[LEARNED] {command}")

    return True