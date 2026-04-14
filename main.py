from core.listener import start_listener
from ai.models import warmup_models


def main():
    print("Starting agent...", flush=True)

    # warm up AI models
    warmup_models()

    print("Agent running in background... Press 'A' to activate")

    # start listener
    start_listener()


if __name__ == "__main__":
    main()