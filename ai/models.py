# =====================================================
# ai/models.py
# Gemma 4 Planner + Intent + Dynamic App Awareness
# =====================================================

import ollama
import json
import subprocess

MODEL_NAME = "gemma4"




# =====================================================
# CLEAN RESPONSE
# =====================================================

def clean_response(text):
    if not text:
        return ""

    text = text.strip()
    text = text.replace("```json", "")
    text = text.replace("```", "")
    return text.strip()


# =====================================================
# EXTRACT JSON
# =====================================================

def extract_json(text):
    text = clean_response(text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    try:
        return json.loads(text[start:end + 1])
    except:
        return None


# =====================================================
# OLLAMA CALL
# =====================================================

def call_model(prompt, temperature=0):
    try:
        print("[LLM] sending request...")

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": temperature
            }
        )

        print("[LLM] response received")

        return clean_response(
            response["message"]["content"]
        )

    except Exception as e:
        print("[LLM ERROR]", e)
        return ""


# =====================================================
# GET INSTALLED APPS
# =====================================================

def get_installed_apps():
    try:
        result = subprocess.run(
            ["ls", "/Applications"],
            capture_output=True,
            text=True
        )

        apps = result.stdout.splitlines()

        clean = []

        for app in apps:
            app = app.replace(".app", "").strip()

            if app:
                clean.append(app)

        return clean[:40]   # token safety

    except:
        return []


# =====================================================
# GET ACTIVE APP
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

        return result.stdout.strip()

    except:
        return "Unknown"


# =====================================================
# CONTEXT BLOCK
# =====================================================

def get_system_context():
    apps = get_installed_apps()
    active = get_active_app()

    app_text = ", ".join(apps)

    return f"""
System Context:

Installed apps:
{app_text}

Currently active app:
{active}
"""


# =====================================================
# INTENT CLASSIFIER
# =====================================================

def ask_intent(command):
    prompt = f"""
You are an intent classifier.

Return ONLY valid JSON.

Allowed intents:
- play_music
- pause_music
- watch_youtube
- open_app
- close_app
- search_web
- code_task
- general_task

Allowed categories:
- media
- web
- productivity
- development
- general

Format:
{{
  "intent":"play_music",
  "category":"media"
}}

User command:
{command}
"""

    text = call_model(prompt, temperature=0)

    data = extract_json(text)

    if data:
        return data

    return {
        "intent": "general_task",
        "category": "general"
    }


# =====================================================
# MAIN PLANNER
# =====================================================

def ask_gemma(command):
    context = get_system_context()

    prompt = f"""
You are an AI desktop automation planner for macOS.

{context}

Task:
{command}

Return ONLY valid JSON.

Allowed actions:
- open_app
- press_key
- hotkey
- type
- wait

Rules:
- Prefer installed native apps over websites
- Use only apps from Installed apps list
- Use browser only if no suitable app exists
- Use Arc browser for browser actions
- Every Website(eg: youtube) action must be in new tab: hotkey command+t
- App take time to open - add wait 2 after open_app
- Use shortest correct plan
- No explanation
- No markdown
- press_key = single key
- hotkey = combinations like command+t
- Always complete the task completely like play music means to song should be playing after execution example like this open Spotify + wait + press space
- for website alsways open the browser with hotkey command+t then type url and press enter

Format:
{{
  "steps":[
    {{"action":"open_app","value":"Spotify"}},
    {{"action":"wait","value":"2"}},
    {{"action":"press_key","value":"space"}}
  ]
}}
"""

    return call_model(prompt, temperature=0.2)


# =====================================================
# VALIDATOR
# =====================================================

def ask_supervisor(command, steps):
    prompt = f"""
You are a strict validator.

Task:
{command}

Steps:
{steps}

Answer ONLY YES or NO.

YES if correct.
NO if wrong, redundant, unsafe, incomplete.
"""

    text = call_model(prompt, temperature=0)

    return text.lower().strip()


# =====================================================
# PLAN FIXER
# =====================================================

def ask_supervisor_fix(command, steps):
    context = get_system_context()

    prompt = f"""
You are a plan repair system.

{context}

Task:
{command}

Broken steps:
{steps}

Return ONLY valid JSON.

Allowed actions:
- open_app
- press_key
- hotkey
- type
- wait

Format:
{{
  "steps":[
    {{"action":"open_app","value":"Spotify"}}
  ]
}}
"""

    return call_model(prompt, temperature=0.1)


# =====================================================
# BACKWARD COMPATIBILITY
# =====================================================

def ask_mistral(command):
    return ask_gemma(command)