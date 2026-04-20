AYZN – Local AI Desktop Agent

AYZN is a local-first AI desktop automation agent built for macOS. It converts natural language commands into executable desktop actions such as opening apps, controlling media, launching websites, and automating repetitive workflows.

The project is designed to run privately on your machine using local language models through Ollama.

⸻

Core Idea

Instead of relying on cloud assistants, AYZN works directly on your computer.

You type:

play music
watch youtube
open vscode
open github

AYZN plans the task, executes it, and remembers successful workflows for faster future use.

⸻

Current Features

Local AI Planning

Uses Gemma through Ollama to convert commands into structured desktop steps.

Hierarchical Memory System

AYZN learns successful tasks and stores them in memory.

Memory retrieval layers:

L1 Exact Match
L2 Intent Match
L3 Fuzzy Match
L4 AI Planning Fallback

This allows previously learned commands to run instantly without loading the model every time.

Skill Library

Reusable atomic actions are automatically learned, such as:

open_spotify
open_arc
new_tab
play_pause

Desktop Automation

Supports actions like:

open_app
press_key
hotkey
type
wait

Background Activation

Runs quietly in background and activates on key press.

⸻

Example Commands

play music
pause music
watch youtube
open github
open vscode
open terminal
show memory
show skills
delete memory play music

⸻

Project Structure

AYZN/
├── ai/
│   └── models.py
├── core/
│   └── executor.py
├── memory/
│   ├── manager.py
│   ├── skills.py
│   └── brain.db
├── main.py
├── requirements.txt
└── README.md

⸻

How It Works

User Command
↓
Memory Lookup
↓ (if found)
Instant Execution
or
Memory Miss
↓
Gemma Planning
↓
Execution
↓
Store in Memory

⸻

Requirements

* macOS
* Python 3.10+
* Ollama installed
* Gemma model pulled locally

Install dependencies:

pip install -r requirements.txt

Install model:

ollama pull gemma4

⸻

Run

python main.py

⸻

Memory Management

Inside AYZN:

show memory
clear memory
delete memory play music
show skills
clear skills
delete skill open_spotify

⸻

Why AYZN

AYZN is focused on:

privacy
speed over time
local intelligence
daily usefulness
self-improving workflows

The more you use it, the smarter and faster it becomes.

⸻

Roadmap

Planned future upgrades:

voice control
vision / screenshot understanding
sleep mode / wake mode
task chaining
better app awareness
workflow editor

⸻

Status

Active experimental build. Rapidly evolving.

⸻

Author

Built by Yash.