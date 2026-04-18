# =====================================================
# core/executor.py
# AYZN FINAL RECHECKED EXECUTOR
# Fast Memory First + One Intent Call + One Planner Call
# Memory / Skill Admin Commands Included
# Cleaned + Safe Version
# =====================================================

import pyautogui
import time
import json
import subprocess

from ai.models import ask_gemma, ask_intent
from memory.manager import (
    get_memory,
    save_memory,
    show_memory,
    delete_memory,
    clear_memory
)

from memory.skills import (
    auto_learn_from_steps,
    list_skills,
    delete_skill,
    clear_skills
)


ACTION_DELAY = 0.15


# =====================================================
# ACTIVE APP
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
# WAIT FOR FOCUS
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
# EXTRACT JSON
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
    fixed = []

    for step in steps:
        action = str(step.get("action", "")).strip().lower()
        value = str(step.get("value", "")).strip().lower()

        if not action:
            continue

        value = value.replace("cmd", "command")

        # fix combo wrongly sent as press_key
        if action == "press_key" and "+" in value:
            action = "hotkey"

        # fix single key wrongly sent as hotkey
        if action == "hotkey" and "+" not in value:
            action = "press_key"

        # cap waits
        if action == "wait":
            try:
                wait_time = float(value)
                wait_time = max(0, min(wait_time, 3))
                value = str(wait_time)
            except:
                value = "1"

        # skip empty invalid values
        if action in ["open_app", "press_key", "hotkey", "type"] and not value:
            continue

        fixed.append({
            "action": action,
            "value": value
        })

    return fixed


# =====================================================
# RUN SINGLE STEP
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
# ADMIN COMMANDS
# =====================================================

def handle_admin(command):
    cmd = command.lower().strip()

    # memory controls
    if cmd == "show memory":
        show_memory()
        return True

    if cmd == "clear memory":
        clear_memory()
        return True

    if cmd.startswith("delete memory "):
        target = command[14:].strip()
        delete_memory(target)
        return True

    # skill controls
    if cmd == "show skills":
        list_skills()
        return True

    if cmd == "clear skills":
        clear_skills()
        return True

    if cmd.startswith("delete skill "):
        target = command[13:].strip()
        delete_skill(target)
        return True

    return False


# =====================================================
# MAIN EXECUTION ENTRY
# =====================================================

def smart_execute(command):
    command = command.strip()

    if not command:
        return False

    # ---------------------------------------------
    # ADMIN COMMANDS
    # ---------------------------------------------

    if handle_admin(command):
        return True

    print("Checking memory...")

    # ---------------------------------------------
    # MEMORY FIRST (NO LLM)
    # ---------------------------------------------

    steps = get_memory(command)

    if steps:
        print("Memory hit ⚡")
        execute_steps(steps)
        return True

    # ---------------------------------------------
    # SINGLE INTENT CALL
    # ---------------------------------------------

    meta = ask_intent(command)

    intent = meta.get("intent", "general_task")
    category = meta.get("category", "general")

    print(f"[INTENT] {intent}")
    print(f"[CATEGORY] {category}")

    # ---------------------------------------------
    # SINGLE PLANNER CALL
    # ---------------------------------------------

    print("Trying Gemma ⚡")

    response = ask_gemma(command)

    print(response)

    steps = extract_steps(response)

    if not steps:
        print("[FAILED] No valid steps")
        return False

    # ---------------------------------------------
    # CLEAN PLAN
    # ---------------------------------------------

    steps = clean_steps(steps)

    if not steps:
        print("[FAILED] Invalid cleaned steps")
        return False

    # ---------------------------------------------
    # EXECUTE
    # ---------------------------------------------

    execute_steps(steps)

    # ---------------------------------------------
    # SAVE LEARNED MEMORY
    # ---------------------------------------------

    save_memory(
        command,
        steps,
        intent=intent,
        category=category
    )

    auto_learn_from_steps(steps)

    print(f"[LEARNED] {command}")

    return True