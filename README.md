
# 🌀 NeoVision Overdrive

A **cyberpunk-themed retro game launcher** written entirely in Python.

Designed for **macOS**. Runs like a dream, looks like a terminal from the year 2077, and probably knows more about your ROMs than you do.

---

## 🎮 Features

- **Supports major systems**:  
  GB, GBC, NES, GBA, DS, 3DS, PSP, GameCube, Wii, PS1 and more.
- **Cover art grid view** with animations and posterized aesthetics.
- **Achievements system** with 120+ unlockables (yes, it remembers).
- **Emulator launching** via smart filetype detection.
- **"Game of the Day"** randomizer.
- **Starfield animation** background (because you deserve space).
- **Cyberpunk BIOS-style boot splash.** Because ✨vibes✨.
- It currently does not support SNES or N64
---

## ⚙️ Requirements

- Python 3.9+
- macOS (tested on Apple Silicon and Intel)
- Installed emulators:
  - Dolphin
  - mGBA
  - DeSmuMe
  - Nestopia
  - PPSSPPSDL
  - Azahar (3DS)
  - PyBoy (`pip install pyboy`)
  - Stella, DuckStation, etc.

---

# 📁 Setup

1. **Clone this repo.**

2. **Install dependencies**:

   pip install pygame pillow pyboy


3. **Create your ROM directory:**
   By default, this will be:

   ~/Emu/


4. **Put your ROMs inside that folder.**
   Supported extensions:
   `.gb`, `.gbc`, `.gba`, `.nds`, `.3ds`, `.iso`, `.cue`, `.a26`, `.gcm`, `.nkit.iso`, `.wbfs`, `.cso`, `.gcz`, `.nes`, etc.

5. **(Optional)**: Add a `covers/` folder inside `~/Emu/` with matching PNGs named after the ROM filenames (e.g., `Super Mario Bros.nes` → `Super Mario Bros.png`).

6. **Run it:**

   ```bash
   python main.py
   ```

---

## 🧠 Configuration

The first time you run `main.py`, it will generate a file called:

```
nv_config.json
```

You can edit it to change paths and settings:

```json
{
  "rom_folder": "~/Emu",
  "covers_folder": "covers",
  "ext_emu_dir": "~/Emu/ExtEmu",
  "fullscreen": true
}
```

Yes, it supports `~` in paths. You're welcome.

---

## 🚀 Emulator Integration

NeoVision launches ROMs using their associated emulators. You must have them installed **locally** in the `ext_emu_dir` (default: `~/Emu/ExtEmu`).

File mapping is done automatically based on file extension, with smart guesses for `.iso` based on keywords like "zelda", "mario", "twilight", etc.

---

## 🏆 Achievements

The launcher includes over **120 achievements** tied to:

* Your ROM library
* Launch history
* Genre detection
* Time of day (e.g. "Night Owl", "Early Bird")
* Franchises ("Pokeymawn", "Mega Man", etc.)

Achievements are saved to:

```
achievements.json
```

---

## 🧪 Tips & Notes

* **You must update emulator paths** in `nv_config.json` if you install emulators somewhere else.
* **Achievements are persistent** but not networked (yet).
* **This is a hobby project**, but it's feature-rich and genuinely usable.
* Run it fullscreen or not, depending on your mood and existential dread.

---

## 💀 Known Limitations

* No Windows support (go use RetroArch if you're desperate).
* Hardcoded emulator arguments (configurable in the future maybe).
* No mouse-based save states for PyBoy — you'll need `S` (save) and `L` (load).

