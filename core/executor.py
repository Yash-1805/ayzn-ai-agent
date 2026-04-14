import pyautogui
import time
import json
import subprocess
import re

from ai.models import ask_mistral
from memory.manager import get_memory, save_memory
from memory.skills import save_skill
from system.apps import open_app, handle_install


ACTION_DELAY = 0.1


# ---------------- ACTIVE APP ----------------

def get_active_app():
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip().lower()


def wait_for_app(app_name, timeout=5):
    start = time.time()

    while time.time() - start < timeout:
        active = get_active_app()

        if app_name.lower() in active:
            print(f"[FOCUSED] {active}")
            return True

        time.sleep(0.3)

    print("[FOCUS FAIL]")
    return False


# ---------------- DIRECT COMMAND ----------------

def handle_direct_command(command):
    command = command.lower().strip()

    # open app
    if command.startswith("open "):
        app = command.replace("open ", "").strip()
        return [{"action": "open_app", "value": app}]

    # close app
    if command.startswith("close "):
        return [{"action": "hotkey", "value": "command+q"}]

    return None


# ---------------- JSON PARSER ----------------

def extract_json(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            return None

        json_text = match.group().strip()

        if json_text.count("{") > json_text.count("}"):
            json_text += "}"

        return json.loads(json_text)

    except Exception as e:
        print("[JSON FIX ERROR]", e)
        return None


def parse_steps(response):
    data = extract_json(response)

    if not data:
        print("[JSON ERROR]")
        return []

    steps = data.get("steps", [])
    fixed_steps = []

    for step in steps:
        action = step.get("action")
        value = step.get("value")

        if action == "open":
            step = {"action": "open_app", "value": "spotify"}

        if action == "click":
            continue

        fixed_steps.append(step)

    return fixed_steps


# ---------------- SAFETY ----------------

def is_safe_step(step):
    allowed = ["open_app", "press_key", "hotkey", "type", "wait"]
    return step.get("action") in allowed


# ---------------- PLAN VALIDATION ----------------

def is_good_plan(command, steps):
    command = command.lower()

    if "music" in command or "song" in command:
        has_open = any(s["action"] == "open_app" for s in steps)
        has_play = any(
            s["action"] == "press_key" and s["value"] == "space"
            for s in steps
        )
        return has_open and has_play

    return True


# ---------------- PLAN FIX ----------------

def fix_plan(command, steps):
    command = command.lower()

    if "music" in command:
        has_space = any(
            s["action"] == "press_key" and s["value"] == "space"
            for s in steps
        )

        if not has_space:
            print("[AUTO FIX] adding play step")
            steps.append({"action": "press_key", "value": "space"})

    return steps


# ---------------- SKILL EXTRACTION ----------------

def extract_and_save_skills(steps):
    for step in steps:
        action = step.get("action")
        value = step.get("value")

        if action == "open_app":
            save_skill(f"open_{value.lower()}", [step])

        elif action == "press_key" and value == "space":
            save_skill("play_pause", [step])


# ---------------- EXECUTION ----------------

def execute_steps(steps):
    print("\n[EXECUTION START]")

    for step in steps:
        if not is_safe_step(step):
            print("[BLOCKED STEP]", step)
            continue

        action = step["action"]
        value = step.get("value")

        print(f"[STEP] {step}")

        try:
            if action == "open_app":
                success = open_app(value)

                if not success:
                    handle_install(value)
                else:
                    wait_for_app(value)
                    time.sleep(0.5)

            elif action == "press_key":
                pyautogui.press(value)

            elif action == "hotkey":
                pyautogui.hotkey(*value.split("+"))

            elif action == "type":
                pyautogui.write(value, interval=0.05)

            elif action == "wait":
                time.sleep(float(value))

        except Exception as e:
            print("[STEP ERROR]", e)

        time.sleep(ACTION_DELAY)

    print("[EXECUTION END]\n")


# ---------------- MAIN ----------------

def smart_execute(command):
    command = command.strip().lower()

    if not command:
        print("[EMPTY COMMAND]")
        return False

    print("Checking memory...")

    # -------- DIRECT COMMAND --------
    direct_steps = handle_direct_command(command)

    if direct_steps:
        print("[DIRECT COMMAND ⚡]")
        execute_steps(direct_steps)
        return True

    # -------- MEMORY --------
    steps = get_memory(command)

    if steps:
        print("Memory hit ⚡")
        steps = fix_plan(command, steps)
        execute_steps(steps)
        return True

    # -------- AI --------
    print("Trying Mistral ⚡")

    response = ask_mistral(command)
    print("Mistral response:\n", response)

    steps = parse_steps(response)

    if not steps:
        print("[FAILED] No valid steps")
        return False

    # -------- FIX --------
    steps = fix_plan(command, steps)

    # -------- EXECUTE --------
    execute_steps(steps)

    # -------- SKILLS --------
    extract_and_save_skills(steps)

    # -------- SAVE MEMORY --------
    if is_good_plan(command, steps):
        save_memory(command, steps)
        print(f"Auto-learned ⚡ → {command}")
    else:
        print("[SKIPPED SAVE] incomplete plan")

    return True