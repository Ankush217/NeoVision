#!/opt/homebrew/bin/python3
import sys
import os
import pygame
import subprocess
import time
from pyboy import PyBoy
from pyboy.utils import WindowEvent

# --- Constants ---
ROM_DIR = "/Users/apple/Emu/"
EXT_EMU_DIR = "/Users/apple/Emu/ExtEmu"

def smart_iso_emulator(rom):
    rom_lc = rom.lower()
    wii_keywords = ["mario", "zelda", "metroid", "wii", "galaxy", "samus", "bowser", "nkit", "twilight", "resort", "donkey"]
    return (
        "Dolphin.app/Contents/MacOS/Dolphin"
        if any(keyword in rom_lc for keyword in wii_keywords)
        else "PPSSPPSDL.app/Contents/MacOS/PPSSPPSDL"
    )

def smart_iso_args(rom):
    rom_lc = rom.lower()
    wii_keywords = ["mario", "zelda", "metroid", "wii", "galaxy", "samus", "bowser", "nkit", "twilight", "resort", "donkey"]
    return ["-e", rom] if any(keyword in rom_lc for keyword in wii_keywords) else [rom]

EMULATOR_MAP = {
    ".sfc":  {"emulator": "Snes9x.app/Contents/MacOS/Snes9x", "args": lambda rom: [rom]},
    ".smc":  {"emulator": "Snes9x.app/Contents/MacOS/Snes9x", "args": lambda rom: [rom]},
    ".gba":  {"emulator": "mGBA.app/Contents/MacOS/mGBA", "args": lambda rom: [rom]},
    ".nds":  {"emulator": "DeSmuMe.app/Contents/MacOS/DeSmuME", "args": lambda rom: [rom]},
    ".n64":  {"emulator": "mupen64plus-bundle-osx-2.6.0/mupen64plus.app", "args": lambda rom: [rom]},
    ".z64":  {"emulator": "mupen64plus-bundle-osx-2.6.0/mupen64plus.app/Contents/MacOS/mupen64plus", "args": lambda rom: [rom]},
    ".v64":  {"emulator": "mupen64plus-bundle-osx-2.6.0/mupen64plus.app", "args": lambda rom: [rom]},
    ".bin":  {"emulator": "DuckStation.app/Contents/MacOS/duckstation", "args": lambda rom: [rom]},
    ".cue":  {"emulator": "DuckStation.app/Contents/MacOS/duckstation", "args": lambda rom: [rom]},
    ".a26":  {"emulator": "Stella.app/Contents/MacOS/stella", "args": lambda rom: [rom]},
    ".nes":  {"emulator": "nestopia.app/Contents/MacOS/nestopia", "args": lambda rom: [rom]},
    ".3ds":  {"emulator": "Azahar.app/Contents/MacOS/azahar", "args": lambda rom: [rom]},
    ".gcm":  {"emulator": "Dolphin.app/Contents/MacOS/Dolphin", "args": lambda rom: ["-e", rom]},
    ".wbfs": {"emulator": "Dolphin.app/Contents/MacOS/Dolphin", "args": lambda rom: ["-e", rom]},
    ".nkit.iso": {"emulator": "Dolphin.app/Contents/MacOS/Dolphin", "args": lambda rom: ["-e", rom]},
    ".gcz": {"emulator": "Dolphin.app/Contents/MacOS/Dolphin", "args": lambda rom: ["-e", rom]},
    ".iso": {"emulator": smart_iso_emulator, "args": smart_iso_args},
    ".cso": {"emulator": "PPSSPPSDL.app/Contents/MacOS/PPSSPPSDL", "args": lambda rom: [rom]},
}

def run_emulator(game):
    rom_path = os.path.join(ROM_DIR, game)
    if not os.path.exists(rom_path):
        print("Error: ROM file not found at", rom_path)
        return

    if game.endswith(('.gb', '.gbc')):
        pygame.init()
        screen = pygame.display.set_mode((160, 144))
        pygame.display.set_caption(game)
        emulator = PyBoy(rom_path)
        emulator.set_emulation_speed(1)
        save_state_path = os.path.join(ROM_DIR, f"{game}.state")

        key_map = {
            pygame.K_RETURN: WindowEvent.PRESS_BUTTON_START,
            pygame.K_BACKSPACE: WindowEvent.PRESS_BUTTON_SELECT,
            pygame.K_a: WindowEvent.PRESS_BUTTON_A,
            pygame.K_b: WindowEvent.PRESS_BUTTON_B,
            pygame.K_UP: WindowEvent.PRESS_ARROW_UP,
            pygame.K_DOWN: WindowEvent.PRESS_ARROW_DOWN,
            pygame.K_LEFT: WindowEvent.PRESS_ARROW_LEFT,
            pygame.K_RIGHT: WindowEvent.PRESS_ARROW_RIGHT,
        }

        key_release_map = {
            pygame.K_RETURN: WindowEvent.RELEASE_BUTTON_START,
            pygame.K_BACKSPACE: WindowEvent.RELEASE_BUTTON_SELECT,
            pygame.K_a: WindowEvent.RELEASE_BUTTON_A,
            pygame.K_b: WindowEvent.RELEASE_BUTTON_B,
            pygame.K_UP: WindowEvent.RELEASE_ARROW_UP,
            pygame.K_DOWN: WindowEvent.RELEASE_ARROW_DOWN,
            pygame.K_LEFT: WindowEvent.RELEASE_ARROW_LEFT,
            pygame.K_RIGHT: WindowEvent.RELEASE_ARROW_RIGHT,
        }

        pressed_keys = set()
        running = True
        clock = pygame.time.Clock()

        while running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        with open(save_state_path, "wb") as f:
                            emulator.save_state(f)
                        print("Game saved!")
                    elif event.key == pygame.K_l and os.path.exists(save_state_path):
                        with open(save_state_path, "rb") as f:
                            emulator.load_state(f)
                        print("Game loaded!")
                    elif event.key in key_map and event.key not in pressed_keys:
                        emulator.send_input(key_map[event.key])
                        pressed_keys.add(event.key)
                elif event.type == pygame.KEYUP and event.key in key_release_map:
                    if event.key in pressed_keys:
                        emulator.send_input(key_release_map[event.key])
                        pressed_keys.remove(event.key)

            emulator.tick()

        pygame.quit()
        emulator.stop()
        return

    else:
        ext = None
        for key in EMULATOR_MAP.keys():
            if game.lower().endswith(key):
                ext = key
                break

        if ext in EMULATOR_MAP:
            emu_info = EMULATOR_MAP[ext]
            emulator_path_raw = emu_info["emulator"]
            emulator_path = (
                os.path.join(EXT_EMU_DIR, emulator_path_raw(game) if callable(emulator_path_raw) else emulator_path_raw)
            )
            args = emu_info["args"](rom_path)

            if not os.path.exists(emulator_path):
                print(f"Error: Emulator not found at {emulator_path}")
                return

            try:
                print(f"Launching {game} using {os.path.basename(emulator_path)}...")
                subprocess.run([emulator_path] + args)
            except Exception as e:
                print("Failed to launch external emulator:", e)
        else:
            print("Unsupported ROM type!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        game = input("Enter the game you want to play (with extension eg. .gb/.gba/.nes/.nds/.iso/.a26): ")
        run_emulator(game)
    else:
        run_emulator(sys.argv[1])
