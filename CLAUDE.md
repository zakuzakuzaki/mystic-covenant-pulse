# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Mystic Covenant Pulse** is a Japanese web application that creates AI-powered summoning creature battles. Users input summoning incantations which Claude Desktop processes to generate 3D STL models and battle statistics. The creatures can then battle each other in an interactive turn-based system.

## Development Commands

```bash
# Start development server with hot-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Alternative startup
python run.py

# Setup Claude Desktop automation coordinates
python scripts/setup_claude.py

# Run tests (framework exists but needs implementation)
pytest tests/
```

## Architecture Overview

### Backend (FastAPI + Python 3.8+)
- **`app/main.py`** - FastAPI application entry point
- **`app/api/`** - REST endpoints for summoning (`summons.py`) and battle system (`battle.py`)
- **`app/services/`** - Core business logic:
  - `claude_controller.py` - Automates Claude Desktop via `pyautogui` for 3D model generation
  - `file_manager.py` - Manages UUID-based asset storage in `assets/` directory
- **`app/core/config.py`** - Configuration management

### Frontend (Vanilla JS + Three.js)
- **`static/index.html`** - Main game interface
- **`static/js/`** - JavaScript modules:
  - `game.js` - Game logic and UI interactions
  - `api.js` - FastAPI communication
  - `3d-viewer.js` - Three.js STL model rendering with orbital controls

### Data Flow
1. User inputs Japanese summoning incantation
2. Backend automates Claude Desktop to generate 3D STL model and creature stats
3. Assets stored in `assets/{uuid}/` with `model.stl`, `status.json`, `summon_status.json`
4. Frontend renders 3D models and enables battle interactions
5. Battle commands processed through Claude Desktop for damage calculation

## Key Technical Components

### Claude Desktop Integration
- **Automation Method**: GUI automation using `pyautogui` with position-based clicking
- **Japanese Text Handling**: Clipboard operations via `pyperclip` for proper Unicode support
- **Configuration**: Mouse coordinates stored in `config/claude_desktop_config.json`
- **Prompting System**: Detailed prompts for consistent Blender STL generation and battle mechanics

### Asset Management
- **Structure**: UUID-based directories under `assets/`
- **Files Per Creature**: 
  - `model.stl` - Generated 3D model
  - `status.json` - Creature stats (name, HP, special moves, description)
  - `summon_status.json` - Generation status tracking
- **Background Processing**: Long-running Claude Desktop operations handled as FastAPI background tasks

### 3D Rendering
- **Library**: Three.js for STL model loading and display
- **Features**: Orbital camera controls, real-time rendering, battle scene visualization
- **Integration**: Direct STL file serving from `assets/` directory

## Configuration Files

- **`config/app_config.json`** - Server settings, CORS, application metadata
- **`config/claude_desktop_config.json`** - Mouse coordinates for GUI automation
- **`requirements.txt`** - Python dependencies including FastAPI, uvicorn, pyautogui

## Development Notes

### Critical Dependencies
- `pyautogui>=0.9.54` - Claude Desktop automation (screen coordinates sensitive)
- `pyperclip>=1.8.2` - Japanese text clipboard handling
- `fastapi>=0.104.0` and `uvicorn[standard]>=0.24.0` - Web framework

### Important Considerations
- **Setup Required**: Run `python scripts/setup_claude.py` to configure Claude Desktop coordinates before first use
- **GUI Automation**: Application requires Claude Desktop to be running and accessible
- **Japanese Support**: Full Unicode handling throughout for Japanese incantations and descriptions
- **File System**: Local storage model - assets directory grows with each summoning

### Current Limitations
- Hardcoded damage calculation in battle system (placeholder values)
- Limited error handling for Claude Desktop automation failures
- No persistence layer beyond file system storage
- Single-user design (no multi-user session management)

## Testing Strategy

Test structure exists in `tests/` directory but requires implementation. Key areas needing coverage:
- Claude Desktop automation reliability
- STL file generation and validation
- Battle system mechanics
- API endpoint responses
- 3D rendering integration