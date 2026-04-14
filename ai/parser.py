# -------------------- CLEAN AI RESPONSE --------------------

def clean_response(res):
    res = res.lower()

    for line in res.split("\n"):
        if line.startswith("open"):
            return line.strip()

    return ""


# -------------------- OVERRIDE HANDLING --------------------

from memory.manager import save_memory
from system.apps import find_app


def handle_override(cmd):
    cmd = cmd.lower().strip()

    # Pattern 1: "use arc for browser"
    if "use" in cmd and "for" in cmd:
        try:
            parts = cmd.split("for")

            app = parts[0].replace("use", "").strip()
            task = parts[1].strip()

            if find_app(app):
                save_memory(task, app)
                print(f"Updated preference ⚡ → {task} = {app}")
                return True

        except:
            pass

    # Pattern 2: "use arc instead"
    if "use" in cmd and "instead" in cmd:
        try:
            app = cmd.replace("use", "").replace("instead", "").strip()

            if find_app(app):
                print(f"Override noted → {app}")
                return True

        except:
            pass

    return False