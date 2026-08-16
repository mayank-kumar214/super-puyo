# Super Puyo

A pixel-art platformer adventure built with Python and Pygame. The game features engaging mechanics like Coyote Time, jump buffering, wall sliding, hazard interactions, particle effects, and a fully functional save system!

## Key Highlights

- **Dynamic Physics & Mechanics**: Wall jumping, fast falling, Coyote Time, and jump buffering for tight, responsive controls.
- **Robust Level Elements**: Moving platforms, falling platforms, bounce trampolines, and directional wind fans.
- **Hazards & Interactions**: Spike pits, fire traps, saws, flying arrows, and crushing rock heads.
- **Save & Resume System**: Progress is saved via `save.json`, allowing you to quit and pick up right where you left off.
- **Polished Feedback**: Procedurally generated sound effects and rich particle systems (dust, sparkles, confetti, screen shake).

---

## Project Structure

```text
super-puyo/
├── assets/                 # Graphics, sprite sheets, and backgrounds
├── main.py                 # Game loop and state machine
├── player.py               # Player physics and state
├── collisions.py           # Collision detection and response
├── objects.py              # Level elements and hazards
├── levels.py               # Level design maps and loader
├── menu.py                 # Main Menu, Pause Menu, and Transitions
├── particles.py            # Visual effects system
├── sound.py                # Procedurally generated audio
├── settings.py             # Global constants
├── utils.py                # Asset loading utilities
├── .gitignore              # Ignored files (including save data)
├── requirements.txt        # Dependencies
└── README.md               # Project documentation
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pygame` (2.6.1 or later)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mayank-kumar214/super-puyo.git
   cd super-puyo
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Playing the Game

To launch the game, run the root script from your terminal:

```bash
python main.py
```

### Controls

| Action | Key(s) | Description |
|--------|--------|-------------|
| **Move Left** | `Left Arrow` / `A` | Run left |
| **Move Right** | `Right Arrow` / `D` | Run right |
| **Jump** | `Spacebar` / `Up Arrow` / `W` | Jump (can double jump!) |
| **Fast Fall** | `Down Arrow` / `S` | Increase gravity to fall faster |
| **Wall Jump** | `Jump` while sliding | Jump off walls while touching them |
| **Pause Menu** | `ESC` | Pause the game to Resume, Restart, or Save & Quit |

---

## Game Mechanics

### Checkpoints & Damage
- **Hazards**: Touching a trap (like a saw or fire) will deduct 1 heart and grant you brief invincibility, allowing you to walk through the trap without teleporting.
- **Pits**: Falling off the bottom of the screen deducts 1 heart and teleports you back to the last safe, solid ground you stood on.
- **Game Over**: Losing all 3 hearts results in a Game Over, allowing you to restart the current level.

### Save System
- Pausing and selecting **SAVE & QUIT** will store your current level, score, fruits collected, and remaining health into a `save.json` file.
- The Main Menu will display a **CONTINUE** button if a save file exists.
- Beating the final level or suffering a Game Over automatically deletes the save file.

---

## 👨‍💻 Author

Built as a professional game development showcase.

## 📄 License

MIT License - Open source and free to use
---

⭐ **Star this repo if you found it helpful!** ⭐
