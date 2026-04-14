from pynput import keyboard
from core.executor import smart_execute


def activate_agent():
    print("AYZN Activated ⚡", flush=True)

    while True:
        cmd = input(">>> ").strip()

        if cmd.lower() == "exit":
            print("Going to sleep...\n")
            break

        success = smart_execute(cmd)

        if not success:
            print("I need to learn this from internet...")


def on_press(key):
    try:
        if key.char == 'A':
            activate_agent()
    except:
        pass


def start_listener():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()