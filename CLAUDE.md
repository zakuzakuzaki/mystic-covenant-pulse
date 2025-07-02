# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Mystic Covenant Pulse** is a Japanese web application that creates AI-powered summoning creature battles. Users input summoning incantations which Claude Desktop processes to generate 3D STL models and battle statistics. The creatures can then battle each other in an interactive turn-based system.

## Development Commands

```bash
# Setup virtual environment (recommended)
python -m venv .env
# Windows: .env\Scripts\activate
# macOS/Linux: source .env/bin/activate
pip install -r requirements.txt

# Start development server (with hot-reload)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Start production server (no hot-reload)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# Alternative startup (uses config settings)
python run.py

# Frontend development (TypeScript compilation)
cd frontend
npm install                    # Install dependencies
npm run build                  # One-time TypeScript compilation
npm run watch                  # Auto-rebuild on file changes
npm run clean                  # Clean compiled JS files

# Setup Claude Desktop automation coordinates (required before first use)
python scripts/setup_claude.py

# Test MCP result submission (for debugging)
python scripts/send_attack_result.py "炎の剣が敵を貫く！" -50
python scripts/send_finish_comment.py "勝利の光よ、全てを照らせ！"

# Run tests (tests directory needs to be created)
pytest tests/

# Code quality checks (if needed)
black app/                     # Format Python code
isort app/                     # Sort imports
flake8 app/                    # Lint Python code
```

## Architecture Overview

### Backend (FastAPI + Python 3.8+)
- **`app/main.py`** - FastAPI application entry point with MCP router integration
- **`app/api/`** - REST endpoints:
  - `summons.py` - Creature summoning and status tracking
  - `battle.py` - Battle system with MCP result endpoints
  - `mcp.py` - MCP result management and queue operations
  - `models.py` - Pydantic models for type safety and validation
- **`app/services/`** - Core business logic (機能別分割済み):
  - `claude_controller.py` - 統合クラス（各コントローラーへの委譲）
  - `claude_desktop_client.py` - Claude Desktop GUI自動化クライアント
  - `summon_controller.py` - 召喚獣生成処理専用コントローラー
  - `battle_controller.py` - バトル処理専用コントローラー
  - `mcp_controller.py` - MCP結果処理専用コントローラー
  - `mcp_manager.py` - Single-item queue manager for Claude Desktop outputs
  - `file_manager.py` - Manages UUID-based asset storage in `assets/` directory
- **`app/core/`** - Core application components:
  - `config.py` - Configuration management
  - `constants.py` - Application constants (timing, prompts, defaults)
  - `exceptions.py` - Unified exception classes

### Frontend (TypeScript + Three.js)
- **Development Environment**: TypeScript in `frontend/src/` compiled to `static/js/`
- **`frontend/src/`** - TypeScript source files:
  - `main.ts` - Entry point and DOM ready initialization
  - `game.ts` - Game logic and UI interactions
  - `api.ts` - FastAPI communication with type safety
  - `3d-viewer.ts` - Three.js STL model rendering with orbital controls
  - `types.ts` - Shared TypeScript type definitions
  - `constants.ts` - Frontend constants (MCP config, UI settings)
- **`static/js/`** - Compiled JavaScript output (do not edit directly)
- **`static/index.html`** - Main game interface

### Data Flow
1. User inputs Japanese summoning incantation
2. Backend automates Claude Desktop to generate 3D STL model and creature stats
3. Assets stored in `assets/{uuid}/` with `model.stl`, `status.json`, `summon_status.json`
4. Frontend renders 3D models and enables battle interactions
5. Battle commands processed through Claude Desktop for damage calculation

## Key Technical Components

### MCP (Model Context Protocol) Integration
- **Primary Architecture**: FastAPI server with MCP endpoints for Claude Desktop communication
- **Result Queue System**: Single-item queue in `assets/mcp_results/` for Claude Desktop outputs
- **Real-time Processing**: Frontend polls `/api/mcp/result/status` and `/api/mcp/result` for live battle results
- **Type Safety**: Structured data models (`ClaudeResultData`, `BattleResult`, `AttackResultData`) with automatic parsing
- **Endpoints**:
  - `POST /api/mcp/results` - Save Claude Desktop results (generic)
  - `POST /api/mcp/results/attack` - Save attack results specifically
  - `POST /api/mcp/results/finish` - Save finish comment results specifically
  - `GET /api/mcp/result` - Retrieve and consume queued results  
  - `GET /api/mcp/result/status` - Check queue status

### Claude Desktop Integration
- **Automation Method**: GUI automation using `pyautogui` with position-based clicking
- **Japanese Text Handling**: Clipboard operations via `pyperclip` for proper Unicode support
- **Configuration**: Mouse coordinates stored in `config/claude_desktop_config.json`
- **Prompting System**: Detailed prompts for consistent Blender STL generation and battle mechanics
- **MCP Workflow**: Attack prompts sent via automation, results retrieved via MCP polling

### Battle System Architecture
- **Dual Processing**: Traditional API fallback with MCP result prioritization
- **Attack Flow**: 
  1. `/api/battle/attack` triggers Claude Desktop automation
  2. Frontend polls for MCP results (30 attempts, 1s intervals)
  3. Structured damage/HP calculations applied to game state
  4. Fallback to API dummy results if MCP times out
- **Type Handling**: Automatic detection and parsing of `battle_result`, `attack`, `creature_generation` types

### Asset Management
- **Structure**: UUID-based directories under `assets/`
- **Files Per Creature**: 
  - `model.stl` - Generated 3D model
  - `status.json` - Creature stats (name, HP, special moves, description)
  - `summon_status.json` - Generation status tracking
- **MCP Results**: Temporary storage in `assets/mcp_results/{execution_id}.json`
- **Background Processing**: Long-running Claude Desktop operations handled as FastAPI background tasks

### 3D Rendering
- **Library**: Three.js for STL model loading and display
- **Features**: Orbital camera controls, real-time rendering, battle scene visualization
- **Integration**: Direct STL file serving from `assets/` directory

## Configuration Files

- **`config/app_config.json`** - Server settings, CORS, application metadata
- **`config/claude_desktop_config.json`** - Mouse coordinates for GUI automation (gitignored)
- **`requirements.txt`** - Python dependencies including FastAPI, uvicorn, pyautogui
- **`frontend/package.json`** - Node.js dependencies for TypeScript compilation
- **`frontend/tsconfig.json`** - TypeScript compiler configuration
- **`docs/`** - Documentation files including memo.md and protopedia.md

## Development Notes

### Critical Dependencies
- **Backend**: `pyautogui>=0.9.54` (Claude Desktop automation), `pyperclip>=1.8.2` (Japanese text), `fastapi>=0.104.0`, `fastapi-mcp>=0.3.4` (MCP integration)
- **Frontend**: `typescript^5.0.0`, `three^0.160.0`, `@types/three^0.160.0` for 3D rendering
- **Development**: Node.js 16+ required for TypeScript compilation

### Architecture Improvements (Latest Refactoring)
- **Service Layer Separation**: Claude Desktop automation split into specialized controllers
- **Constants Management**: All hardcoded values extracted to `constants.py/ts`
- **Unified Error Handling**: Custom exception hierarchy for better error management
- **Type Safety**: Complete integration of `AttackResultData` replacing legacy `AttackResult`
- **Code Reduction**: ~30% reduction in codebase size through deduplication

### Important Considerations
- **Setup Required**: Run `python scripts/setup_claude.py` to configure Claude Desktop coordinates before first use
- **GUI Automation**: Application requires Claude Desktop to be running and accessible
- **Japanese Support**: Full Unicode handling throughout for Japanese incantations and descriptions
- **File System**: Local storage model - assets directory grows with each summoning
- **Frontend Development**: Always edit TypeScript in `frontend/src/`, never directly edit compiled JS in `static/js/`
- **Build Process**: Frontend changes require compilation (`npm run build` or `npm run watch`)

### Current Status & Implementation Notes
- **MCP Integration**: Fully implemented with structured data parsing and frontend polling
- **Battle System**: Real-time Claude Desktop results with API fallback for reliability
- **Type Safety**: Complete Pydantic model coverage for all MCP data types
- **Queue Management**: Single-item MCP result queue prevents accumulation
- **Error Handling**: Comprehensive fallback system for Claude Desktop automation failures
- **File Management**: UUID-based storage with automatic cleanup for MCP results

### Current Limitations
- No persistence layer beyond file system storage
- Single-user design (no multi-user session management)  
- GUI automation dependent on Claude Desktop positioning

## Testing Strategy

Test directory (`tests/`) needs to be created. Key areas needing coverage:
- Claude Desktop automation reliability
- STL file generation and validation
- Battle system mechanics
- API endpoint responses
- 3D rendering integration