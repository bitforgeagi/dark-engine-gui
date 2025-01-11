# Dark Engine GUI

This project began in 2024 as a private app for BitForge Dynamics, designed for testing Ollama models in our R&D workflows. As we refined our internal systems and transitioned to a new architecture in 2025, we saw an opportunity to share this earlier version with the community. Rather than letting it fade into obsolescence, we decided to release it as a free, open-source educational tool for students and hobbyists interested in private AI development. This guide provides a hands-on introduction to building a modern, dark-themed chat interface for Ollama using Python and CustomTkinter—because the future of AI starts with sharing knowledge and tools.


<img width="988" alt="Screenshot 2025-01-11 at 2 30 31 PM" src="https://github.com/user-attachments/assets/7570b208-2c35-4e4e-af5c-b07520e418af" />


Read our [Blog](https://www.bitforgedynamics.com/blog) to create Dark Engine GUI with a step-by-step guide!

## Features

- 🌙 Modern dark theme interface
- 💬 Chat with multiple Ollama models
- 📁 Organize chats in folders
- 💾 Automatic chat history saving
- ⚡ Real-time token counting
- 🎨 Customizable theme colors
- 📊 Server status monitoring
- 🔄 Dynamic message loading
- ⌨️ Code block support with syntax highlighting
- 📏 Adjustable input area

## Prerequisites

- [Ollama](https://ollama.com) must be installed and running on your system

## Building from Source

1. Clone the repository:
```bash
git clone https://github.com/bitforgeagi/dark-engine-gui.git
cd dark-engine-gui
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Build for your platform:

```bash
python build.py
```

This will create:
- macOS: `dist/Dark-Engine-GUI-[version].dmg`
- Windows: `dist/Dark Engine GUI.exe`
- Linux: `dist/Dark-Engine-GUI.AppImage`

## Development

Requirements:
- Python 3.8+
- Required packages: `pip install -r requirements.txt`

Development setup:
```bash
# Clone repository
git clone https://github.com/bitforgeagi/dark-engine-gui.git
cd dark-engine-gui

# Create virtual environment
python -m venv venv  # May need to use python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py
```

## Guide

- Once you build the app or create a virtual environment, you should be greeted by the Welcome Window, make sure to have ollama downloaded. Models can be downloaded from the Welcome Window

<img width="836" alt="DEGUI- Welcome Window" src="https://github.com/user-attachments/assets/f6a595a2-df53-4ea4-b603-077b2b1cba0e" />

- Create New Chats in the Quick Chats main-folder OR create a folder to store specific chats

<img width="991" alt="DEGUI - Chat Window" src="https://github.com/user-attachments/assets/02fada9a-68c2-4cbf-acb3-f0f18377b31e" />


- While the sidebar menu is open, click on the settings gear to change appearance, model, and create agents

<img width="987" alt="DEGUI - Color Change" src="https://github.com/user-attachments/assets/05fbabc6-4402-470f-bce3-1fdd702ac868" />

- Change the font or font-size in the chat from the appearance tab

<img width="992" alt="DEGUI - Font Change" src="https://github.com/user-attachments/assets/c80d2e40-55eb-4721-bdca-d148f84ee198" />

- Create an agent with a prompt template or customize the system prompt

<img width="992" alt="DEGUI - Agent Creator" src="https://github.com/user-attachments/assets/7826a4f0-c03d-4c66-bb1d-65da4d84e774" />

## License

[MIT License](LICENSE) - See LICENSE file for details.

## Acknowledgments

- [Ollama](https://github.com/jmorganca/ollama) for the amazing local LLM runtime
- [llama.cpp](https://github.com/ggerganov/llama.cpp) for the efficient LLM inference engine powering Ollama
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI components

## Authors:
- [BitForge Dynamics](https://www.bitforgedynamics.com) | Brock Daily

