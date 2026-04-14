import os
import subprocess

APPLICATIONS_PATH = "/Applications"


def normalize(text):
    return text.lower().replace(" ", "")


def find_app(app_name):
    app_name = normalize(app_name)

    matches = []

    for app in os.listdir(APPLICATIONS_PATH):
        if not app.endswith(".app"):
            continue

        if app_name in normalize(app):
            matches.append(app)

    for app in matches:
        if app_name == normalize(app):
            return app

    if matches:
        matches.sort(key=lambda x: len(x))
        return matches[0]

    return None


def open_app(app_name):
    app = find_app(app_name)

    if app:
        subprocess.run(["open", "-a", app])
        print(f"Opened {app} ⚡")
        return True

    return False


def handle_install(app_name):
    choice = input(f"{app_name} not found ❌\nSearch online? (y/n): ")

    if choice.lower() == 'y':
        query = f"{app_name} mac download"
        subprocess.run(["open", f"https://www.google.com/search?q={query}"])