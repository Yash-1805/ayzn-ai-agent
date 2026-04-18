from core.listener import start_listener
import ollama


def warmup_models():
    print("Warming up AI...", flush=True)

    ollama.chat(
        model='gemma4',
        messages=[
            {
                'role': 'user',
                'content': 'hi'
            }
        ]
    )

    print("AI Ready ⚡", flush=True)


def main():
    print("Starting agent...", flush=True)

    # warm up AI models
    warmup_models()

    print("Agent running in background... Press 'A' to activate")

    # start listener
    start_listener()


if __name__ == "__main__":
    main()