AYZN

AYZN is a local macOS AI desktop agent that automates tasks using keyboard control, memory learning, and LLM-driven planning.

⸻

Features
	•	Keyboard-triggered execution (background agent)
	•	Memory system using TF-IDF and SQLite
	•	Learns from previous commands
	•	LLM fallback using Mistral via Ollama
	•	Direct command execution (fast path, no AI)
	•	Step-level skill learning
	•	Safe execution with validated actions

⸻

Architecture

User Command
→ Direct Command (fast path)
→ Memory (learned tasks)
→ LLM (Mistral fallback)
→ Execution Engine

⸻

Installation

1. Clone the repository

git clone https://github.com/Yash-1805/ayzn-ai-agent.git
cd ayzn-ai-agent


⸻

2. Create virtual environment

python3 -m venv venv
source venv/bin/activate


⸻

3. Install dependencies

pip install -r requirements.txt


⸻

4. Install Ollama

Download from: https://ollama.com

⸻

5. Pull Mistral model

ollama pull mistral


⸻

Run

python main.py

Press:

j

to activate the agent.

⸻

Example Commands

play music
open chrome
open terminal
search youtube


⸻

How It Works
	•	Direct commands are executed instantly
	•	Memory reuses previously successful tasks
	•	LLM generates steps for new tasks
	•	Executor runs validated keyboard actions

⸻

Supported Actions

open_app: <app>
press_key: <key>
hotkey: key+key
type: <text>
wait: <seconds>


⸻

Project Structure

core/
  executor.py
  listener.py

system/
  apps.py

memory/
  manager.py
  db.py
  skills.py

ai/
  models.py

main.py
requirements.txt


⸻

Limitations
	•	macOS only
	•	No GUI yet
	•	No voice control yet
	•	Limited multi-step reasoning

⸻

Roadmap
	•	Logging system
	•	Floating UI
	•	Voice control
	•	Advanced planning
    •	Vision support (OCR + UI understanding)
	•	Autonomous workflows

⸻

Version

v0.5 (Alpha)

⸻

License

Not specified yet.