import ollama

def warmup_models():
    print("Warming up AI...", flush=True)

    ollama.chat(model='mistral', messages=[{'role': 'user', 'content': 'hi'}])

    print("AI Ready ⚡", flush=True)


def ask_mistral(cmd):
    print("[LLM] sending request...")

    try:
        response = ollama.generate(
            model='mistral',
            prompt=f"""
You are a macOS automation agent.

ALLOWED actions ONLY:
- open_app
- press_key
- hotkey
- type
- wait

STRICT RULES:
- NEVER use "open"
- NEVER use "click"
- NEVER use file paths
- ALWAYS use open_app for apps
- For music → ALWAYS use spotify
- YouTube must open in Arc
- YouTube is NOT an app → ALWAYS open in browser
- Use Arc for websites
- NEVER invent apps
-to open any website first open Arc, then cmd+t, then type the URL, then press enter

OUTPUT FORMAT (STRICT JSON):
{{
  "steps": [
    {{"action": "open_app", "value": "spotify"}},
    {{"action": "press_key", "value": "space"}}
  ]
}}

Command: {cmd}
""",
            options={
                "temperature": 0,
                "num_predict": 150
            }
        )

        print("[LLM] response received")

        return response["response"].strip()

    except Exception as e:
        print("[LLM ERROR]", e)
        return ""

# def ask_mistral(cmd):
#     response = ollama.chat(
#         model='mistral',
#         messages=[{
#             'role': 'user',
#             'content': f"""
# You are a macOS automation agent.

# Rules:
# - YouTube is NOT an app → ALWAYS open in browser
# - Use Arc for websites
# - NEVER invent apps

# STRICT OUTPUT FORMAT:
# Only JSON:
# {{
#   "steps": [
#     {{"action": "...", "value": "..."}}
#   ]
# }}

# Allowed actions:
# open_app, press_key, hotkey, type, wait

# Examples:

# Command: play music
# {{
#   "steps": [
#     {{"action": "open_app", "value": "spotify"}},
#     {{"action": "press_key", "value": "space"}}
#   ]
# }}

# Command: watch youtube
# {{
#   "steps": [
#     {{"action": "open_app", "value": "Arc"}},
#     {{"action": "wait", "value": 1}},
#     {{"action": "type", "value": "youtube.com"}},
#     {{"action": "press_key", "value": "enter"}}
#   ]
# }}

# Command: "{cmd}"
# """
    #     }],
    #     options={"temperature": 0}
    # )

    # return response['message']['content'].strip()


# def ask_llama(cmd):
#     response = ollama.chat(
#         model='llama3',
#         messages=[{
#             'role': 'user',
#             'content': f"""
# You are an automation planner.

# Convert the command into clear executable steps.

# Command: "{cmd}"

# Rules:
# - Output ONLY steps
# - Each step on new line
# - Use simple actions like:
#   - open_app: Spotify
#   - press_key: space
#   - switch_app
# - Be precise

# Example:
# open_app: Spotify
# press_key: space
# """
#         }],
#         options={"num_predict": 10}
#     )
#     return response['message']['content'].strip()