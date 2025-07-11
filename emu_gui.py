import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageOps, ImageFont
import os
import emu
import random
import time
from math import sin
import sys
import json
from collections import defaultdict

# --- Constants ---
ROM_EXTENSIONS = (
    ".gb", ".gbc", ".nes", ".gba", ".nds", ".cue", ".a26", ".gcm",
    ".nkit.iso", ".wbfs", ".3ds", ".iso", ".cso", ".gcz"
)
ROM_FOLDER = "/Users/apple/Emu"
COVERS_FOLDER = os.path.join(ROM_FOLDER, "covers")
THUMB_SIZE = (300, 300)
BG_COLOR = "#0a0a1a"
ACCENT_COLOR = "#00ffcc"
TEXT_COLOR = "#ffffff"
SECONDARY_COLOR = "#ff00aa"
ACH_FILE = "achievements.json"

cover_thumbnails = []
stars = []

# --- System-Wide Achievements ---
SYSTEM_ACHIEVEMENTS = {
    "Pokeymawn": lambda roms, _: sum("pokemon" in r.lower() for r in roms) >= 1,
    "Hyrule’s King": lambda roms, _: sum("zelda" in r.lower() for r in roms) >= 12,
    "Are You OK?": lambda _, launches: any(count >= 2 for count in launches.values()),
    "Assassin": lambda roms, launches: any("assassin" in rom.lower() and count >= 3
                                           for rom, count in launches.items()),
    "Collector": lambda roms, _: len(roms) >= 50,
    "Mega Collector": lambda roms, _: len(roms) >= 200,
    "ROM Hoarder": lambda roms, _: len(roms) >= 500,
    "First Launch": lambda _, launches: sum(launches.values()) >= 1,
    "Ten Launches": lambda _, launches: sum(launches.values()) >= 10,
    "Hundred Launches": lambda _, launches: sum(launches.values()) >= 100,
    "Night Owl": lambda _, __: 0 <= time.localtime().tm_hour <= 4,
    "Early Bird": lambda _, __: 5 <= time.localtime().tm_hour <= 7,
    "Weekend Warrior": lambda _, __: time.localtime().tm_wday in (5, 6),
    "Retro Fan": lambda roms, _: any(r.lower().endswith(".nes") for r in roms),
    "Handheld Hero": lambda roms, _: any(r.lower().endswith(".gb") or r.lower().endswith(".gba") for r in roms),
    "Disc Spinner": lambda roms, _: any(r.lower().endswith(".iso") for r in roms),
    "DS Discoverer": lambda roms, _: any(r.lower().endswith(".nds") for r in roms),
    "Cube Collector": lambda roms, _: any(r.lower().endswith(".gcm") for r in roms),
    "Atari Addict": lambda roms, _: any(r.lower().endswith(".a26") for r in roms),
    "3DS Explorer": lambda roms, _: any(r.lower().endswith(".3ds") for r in roms),
    "Wii Wizard": lambda roms, _: any(r.lower().endswith(".wbfs") for r in roms),
    "Game Completionist": lambda _, launches: any(count >= 10 for count in launches.values()),
    "Double Trouble": lambda _, launches: len([c for c in launches.values() if c >= 2]) >= 2,
    "Triple Threat": lambda _, launches: len([c for c in launches.values() if c >= 3]) >= 3,
    "Quad Squad": lambda _, launches: len([c for c in launches.values() if c >= 4]) >= 4,
    "ROM Explorer": lambda roms, _: len(roms) >= 10,
    "ROM Adventurer": lambda roms, _: len(roms) >= 25,
    "ROM Master": lambda roms, _: len(roms) >= 100,
    "Cover Lover": lambda roms, _: sum(os.path.exists(os.path.join(COVERS_FOLDER, os.path.splitext(r)[0]+".png")) for r in roms) >= 10,
    "Cover Collector": lambda roms, _: sum(os.path.exists(os.path.join(COVERS_FOLDER, os.path.splitext(r)[0]+".png")) for r in roms) >= 50,
    "Cover Completionist": lambda roms, _: sum(os.path.exists(os.path.join(COVERS_FOLDER, os.path.splitext(r)[0]+".png")) for r in roms) == len(roms) and len(roms) > 0,
    "Mario Mania": lambda roms, _: any("mario" in r.lower() for r in roms),
    "Sonic Speed": lambda roms, _: any("sonic" in r.lower() for r in roms),
    "Metroidvania": lambda roms, _: any("metroid" in r.lower() for r in roms),
    "Final Fantasy": lambda roms, _: any("final fantasy" in r.lower() for r in roms),
    "Dragon Slayer": lambda roms, _: any("dragon" in r.lower() for r in roms),
    "Mega Man": lambda roms, _: any("mega man" in r.lower() or "megaman" in r.lower() for r in roms),
    "Castlevania": lambda roms, _: any("castlevania" in r.lower() for r in roms),
    "Kirby Collector": lambda roms, _: any("kirby" in r.lower() for r in roms),
    "Donkey Kong": lambda roms, _: any("donkey kong" in r.lower() for r in roms),
    "Street Fighter": lambda roms, _: any("street fighter" in r.lower() for r in roms),
    "Smash Fan": lambda roms, _: any("smash" in r.lower() for r in roms),
    "Fire Emblem": lambda roms, _: any("fire emblem" in r.lower() for r in roms),
    "Mother Earth": lambda roms, _: any("mother" in r.lower() or "earthbound" in r.lower() for r in roms),
    "Advance Wars": lambda roms, _: any("advance wars" in r.lower() for r in roms),
    "Golden Sun": lambda roms, _: any("golden sun" in r.lower() for r in roms),
    "Harvest Moon": lambda roms, _: any("harvest moon" in r.lower() for r in roms),
    "Animal Crossing": lambda roms, _: any("animal crossing" in r.lower() for r in roms),
    "Phoenix Wright": lambda roms, _: any("phoenix wright" in r.lower() for r in roms),
    "Professor Layton": lambda roms, _: any("professor layton" in r.lower() for r in roms),
    "Tetris Master": lambda roms, _: any("tetris" in r.lower() for r in roms),
    "Puzzle Pro": lambda roms, _: any("puzzle" in r.lower() for r in roms),
    "RPG Fanatic": lambda roms, _: sum(any(x in r.lower() for x in ["rpg", "quest", "fantasy", "dragon"]) for r in roms) >= 10,
    "Platformer Pro": lambda roms, _: sum(any(x in r.lower() for x in ["platform", "jump", "run"]) for r in roms) >= 10,
    "Fighting Fan": lambda roms, _: sum(any(x in r.lower() for x in ["fighter", "fight", "brawl"]) for r in roms) >= 5,
    "Racer": lambda roms, _: sum(any(x in r.lower() for x in ["race", "kart", "racer"]) for r in roms) >= 5,
    "Sports Star": lambda roms, _: sum(any(x in r.lower() for x in ["soccer", "football", "basketball", "sports"]) for r in roms) >= 5,
    "Shooter": lambda roms, _: sum(any(x in r.lower() for x in ["shooter", "shoot", "gun"]) for r in roms) >= 5,
    "Strategy Sage": lambda roms, _: sum(any(x in r.lower() for x in ["strategy", "tactics", "wars"]) for r in roms) >= 5,
    "Puzzle Genius": lambda roms, _: sum(any(x in r.lower() for x in ["puzzle", "block", "brain"]) for r in roms) >= 5,
    "Arcade Addict": lambda roms, _: sum(any(x in r.lower() for x in ["arcade", "pacman", "galaga", "asteroids"]) for r in roms) >= 5,
    "Indie Explorer": lambda roms, _: sum("indie" in r.lower() for r in roms) >= 1,
    "Hidden Gem": lambda roms, _: any("gem" in r.lower() for r in roms),
    "Remake Hunter": lambda roms, _: sum("remake" in r.lower() for r in roms) >= 1,
    "Remaster Collector": lambda roms, _: sum("remaster" in r.lower() for r in roms) >= 1,
    "Demo Disc": lambda roms, _: sum("demo" in r.lower() for r in roms) >= 1,
    "Beta Tester": lambda roms, _: sum("beta" in r.lower() for r in roms) >= 1,
    "Prototype Finder": lambda roms, _: sum("proto" in r.lower() for r in roms) >= 1,
    "Japan Only": lambda roms, _: sum("japan" in r.lower() or "(j)" in r.lower() for r in roms) >= 1,
    "Europe Only": lambda roms, _: sum("europe" in r.lower() or "(e)" in r.lower() for r in roms) >= 1,
    "USA Only": lambda roms, _: sum("usa" in r.lower() or "(u)" in r.lower() for r in roms) >= 1,
    "PAL Collector": lambda roms, _: sum("pal" in r.lower() for r in roms) >= 1,
    "NTSC Collector": lambda roms, _: sum("ntsc" in r.lower() for r in roms) >= 1,
    "Unlicensed": lambda roms, _: sum("unlicensed" in r.lower() for r in roms) >= 1,
    "Fan Translation": lambda roms, _: sum("fan" in r.lower() and "trans" in r.lower() for r in roms) >= 1,
    "Hack Hunter": lambda roms, _: sum("hack" in r.lower() for r in roms) >= 1,
    "Homebrew": lambda roms, _: sum("homebrew" in r.lower() for r in roms) >= 1,
    "Multiplayer": lambda roms, _: sum("multi" in r.lower() for r in roms) >= 1,
    "Singleplayer": lambda roms, _: sum("single" in r.lower() for r in roms) >= 1,
    "First Person": lambda roms, _: sum("fps" in r.lower() or "first person" in r.lower() for r in roms) >= 1,
    "Third Person": lambda roms, _: sum("third person" in r.lower() for r in roms) >= 1,
    "Open World": lambda roms, _: sum("open world" in r.lower() for r in roms) >= 1,
    "Sandbox": lambda roms, _: sum("sandbox" in r.lower() for r in roms) >= 1,
    "Simulation": lambda roms, _: sum("sim" in r.lower() for r in roms) >= 1,
    "Pinball Wizard": lambda roms, _: sum("pinball" in r.lower() for r in roms) >= 1,
    "Board Gamer": lambda roms, _: sum("board" in r.lower() for r in roms) >= 1,
    "Card Shark": lambda roms, _: sum("card" in r.lower() for r in roms) >= 1,
    "Music Maestro": lambda roms, _: sum("music" in r.lower() or "rhythm" in r.lower() for r in roms) >= 1,
    "Dance Machine": lambda roms, _: sum("dance" in r.lower() for r in roms) >= 1,
    "Party Animal": lambda roms, _: sum("party" in r.lower() for r in roms) >= 1,
    "Quiz Master": lambda roms, _: sum("quiz" in r.lower() for r in roms) >= 1,
    "Trivia King": lambda roms, _: sum("trivia" in r.lower() for r in roms) >= 1,
    "Educational": lambda roms, _: sum("edu" in r.lower() or "learn" in r.lower() for r in roms) >= 1,
    "Horror Fan": lambda roms, _: sum("horror" in r.lower() for r in roms) >= 1,
    "Survivalist": lambda roms, _: sum("survival" in r.lower() for r in roms) >= 1,
    "Stealthy": lambda roms, _: sum("stealth" in r.lower() for r in roms) >= 1,
    "Detective": lambda roms, _: sum("detective" in r.lower() for r in roms) >= 1,
    "Space Cadet": lambda roms, _: sum("space" in r.lower() for r in roms) >= 1,
    "Sci-Fi Fan": lambda roms, _: sum("sci-fi" in r.lower() or "scifi" in r.lower() for r in roms) >= 1,
    "Fantasy Fan": lambda roms, _: sum("fantasy" in r.lower() for r in roms) >= 1,
    "Western": lambda roms, _: sum("western" in r.lower() for r in roms) >= 1,
    "Ninja": lambda roms, _: sum("ninja" in r.lower() for r in roms) >= 1,
    "Samurai": lambda roms, _: sum("samurai" in r.lower() for r in roms) >= 1,
    "Pirate": lambda roms, _: sum("pirate" in r.lower() for r in roms) >= 1,
    "Robot": lambda roms, _: sum("robot" in r.lower() for r in roms) >= 1,
    "Monster": lambda roms, _: sum("monster" in r.lower() for r in roms) >= 1,
    "Zombie": lambda roms, _: sum("zombie" in r.lower() for r in roms) >= 1,
    "Vampire": lambda roms, _: sum("vampire" in r.lower() for r in roms) >= 1,
    "Alien": lambda roms, _: sum("alien" in r.lower() for r in roms) >= 1,
    "Superhero": lambda roms, _: sum("superhero" in r.lower() for r in roms) >= 1,
    "Villain": lambda roms, _: sum("villain" in r.lower() for r in roms) >= 1,
    "Movie Tie-In": lambda roms, _: sum("movie" in r.lower() for r in roms) >= 1,
    "TV Tie-In": lambda roms, _: sum("tv" in r.lower() for r in roms) >= 1,
    "Comic Book": lambda roms, _: sum("comic" in r.lower() for r in roms) >= 1,
    "Bookworm": lambda roms, _: sum("book" in r.lower() for r in roms) >= 1,
    "Reminisce": lambda _, __: True,  # Always unlocks
    "Speedrunner": lambda _, launches: any(count >= 20 for count in launches.values()),
    "Completionist": lambda _, launches: all(count >= 1 for count in launches.values()) if launches else False,
    "ROM Newbie": lambda _, launches: sum(launches.values()) == 1,
    "ROM Regular": lambda _, launches: sum(launches.values()) >= 25,
    "ROM Veteran": lambda _, launches: sum(launches.values()) >= 250,
    "ROM Addict": lambda _, launches: sum(launches.values()) >= 10000,
    "ROM Tourist": lambda _, launches: len(launches) >= 5,
    "ROM Explorer+": lambda _, launches: len(launches) >= 20,
    "ROM Connoisseur": lambda _, launches: len(launches) >= 50,
    "ROM Guru": lambda _, launches: len(launches) >= 100,
    "ROM Sage": lambda _, launches: len(launches) >= 200,
    "ROM Emperor": lambda _, launches: len(launches) >= 500,
    "ROM King": lambda _, launches: len(launches) >= 1000,
    "ROM Emperor+": lambda _, launches: len(launches) >= 2000,
    "ROM God+": lambda _, launches: len(launches) >= 5000,
}

unlocked_achievements = []
launch_counts = defaultdict(int)

# --- Achievement Logic ---
def load_achievements():
    global unlocked_achievements, launch_counts
    if os.path.exists(ACH_FILE):
        with open(ACH_FILE, "r") as f:
            data = json.load(f)
            unlocked_achievements = data.get("unlocked", [])
            launch_counts.update(data.get("launch_counts", {}))
    else:
        unlocked_achievements.clear()
        launch_counts.clear()

def save_achievements():
    with open(ACH_FILE, "w") as f:
        json.dump({
            "unlocked": unlocked_achievements,
            "launch_counts": dict(launch_counts)
        }, f, indent=2)

def check_and_unlock_achievements():
    roms = get_rom_files()
    for name, condition in SYSTEM_ACHIEVEMENTS.items():
        try:
            if name not in unlocked_achievements and condition(roms, launch_counts):
                unlocked_achievements.append(name)
                print(f"🏆 Achievement Unlocked: {name}")
        except Exception as e:
            print(f"Error checking achievement {name}: {e}")
    save_achievements()

# --- ROM + UI Utilities ---
def get_rom_files():
    return sorted([f for f in os.listdir(ROM_FOLDER) if f.lower().endswith(ROM_EXTENSIONS)])

def type_line(text, delay=0.02):
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def splash_boot():
    for line in ["NeoVision Overdrive BIOS v1.03", "Initializing core modules...",
                 "Detecting input devices...", "Mounting ROM archive...",
                 "Launching interface..."]:
        type_line(line, 0.04)
        time.sleep(0.3)
    time.sleep(1)

def smart_resize_cover(img, size):
    img_ratio = img.width / img.height
    tgt_ratio = size[0] / size[1]
    if img_ratio > tgt_ratio:
        new_h = size[1]; new_w = int(new_h * img_ratio)
    else:
        new_w = size[0]; new_h = int(new_w / img_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - size[0]) // 2
    top = (new_h - size[1]) // 2
    return img.crop((left, top, left + size[0], top + size[1]))

def launch_rom(rom_name):
    path = os.path.join(ROM_FOLDER, rom_name)
    if not os.path.exists(path):
        messagebox.showerror("Error", f"ROM not found:\n{path}")
        return
    launch_counts[rom_name] += 1
    check_and_unlock_achievements()
    emu.run_emulator(path)

def play_selected():
    rom = rom_var.get()
    if rom:
        launch_rom(rom)
    else:
        messagebox.showwarning("No ROM selected", "Please select a ROM.")

# --- Cover Image Handling ---
def load_cover_image(rom_name):
    base = os.path.splitext(rom_name)[0]
    paths = [os.path.join(COVERS_FOLDER, rom_name + ".png"),
             os.path.join(COVERS_FOLDER, base + ".png")]
    for path in paths:
        if os.path.isfile(path):
            img = Image.open(path).convert("RGB")
            img = ImageOps.posterize(img, 3)
            img = smart_resize_cover(img, THUMB_SIZE)
            border = Image.new("RGB", (THUMB_SIZE[0]+4, THUMB_SIZE[1]+4), ACCENT_COLOR)
            border.paste(img, (2,2))
            return ImageTk.PhotoImage(border)

    img = Image.new("RGB", THUMB_SIZE, (16,16,40))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = None
    draw.text((THUMB_SIZE[0]//4, THUMB_SIZE[1]//2-10), "No Cover", fill=ACCENT_COLOR, font=font)
    return ImageTk.PhotoImage(img)

# --- ROM Refresh + Search ---
def refresh_rom_list():
    roms = get_rom_files()
    rom_dropdown['values'] = roms
    if roms:
        rom_dropdown.current(0)
    update_random_highlight()
    refresh_cover_tabs(roms)

def refresh_cover_tabs(roms):
    for w in cover_frame.winfo_children(): w.destroy()
    cover_thumbnails.clear()
    filtered = [r for r in roms if search_var.get().lower() in r.lower()]
    for idx, rom in enumerate(filtered):
        img = load_cover_image(rom)
        cover_thumbnails.append(img)
        frame = tk.Frame(cover_frame, bg=BG_COLOR)
        r, c = divmod(idx, 4)
        frame.grid(row=r, column=c, padx=12, pady=12)
        frame.bind("<Enter>", lambda e, b=frame: b.configure(bg=SECONDARY_COLOR))
        frame.bind("<Leave>", lambda e, b=frame: b.configure(bg=BG_COLOR))
        btn = tk.Button(frame, image=img, relief="flat", bd=0, bg=BG_COLOR,
                        command=lambda r=rom: (rom_var.set(r), launch_rom(r)))
        btn.pack()
        name = rom if len(rom)<=30 else rom[:27]+"..."
        tk.Label(frame, text=name, bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial",10)).pack()

def on_search(*_):
    refresh_cover_tabs(get_rom_files())

def update_random_highlight():
    roms = get_rom_files()
    if not roms:
        highlight_label.config(text="No ROMs Found", fg=SECONDARY_COLOR)
        return
    rom = random.choice(roms)
    path = os.path.join(ROM_FOLDER, rom)
    size = os.path.getsize(path)//1024
    mtime = time.ctime(os.path.getmtime(path))
    highlight_label.config(text=f"🎲 Game of the Day: {rom}  |  {size} KB  |  Modified: {mtime}",
                           fg=ACCENT_COLOR)

# --- Animations ---
def animate_header():
    header.place_configure(y=20 + sin(time.time()*2)*10)
    root.after(50, animate_header)

def create_starfield(num=60):
    for _ in range(num):
        stars.append([random.randint(0,1920), random.randint(0,1080), random.randint(1,3)])

def animate_starfield():
    canvas_bg.delete("star")
    for star in stars:
        star[1] += star[2]
        if star[1] > 1080:
            star[0], star[1] = random.randint(0,1920), 0
        canvas_bg.create_oval(star[0], star[1], star[0]+star[2], star[1]+star[2],
                              fill="#4444ff", outline="", tags="star")
    root.after(50, animate_starfield)

# --- Achievements Tab ---
def populate_achievements_tab():
    for w in ach_tab_frame.winfo_children(): w.destroy()
    if not unlocked_achievements:
        tk.Label(ach_tab_frame, text="No Achievements Yet.", fg=TEXT_COLOR,
                 bg=BG_COLOR, font=("Courier", 16)).pack(pady=20)
        return
    for name in unlocked_achievements:
        tk.Label(ach_tab_frame, text=f"🏆 {name}", bg=BG_COLOR, fg=ACCENT_COLOR,
                 font=("Courier", 14), anchor="w").pack(fill="x", pady=6, padx=20)

# --- GUI Setup ---
root = tk.Tk()
root.title("NeoVision Overdrive")
root.attributes("-fullscreen", True)
root.configure(bg=BG_COLOR)

canvas_bg = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
canvas_bg.place(relwidth=1, relheight=1, x=0, y=0)

header = tk.Label(root, text="💾 NeoVision Overdrive", font=("Courier",28,"bold"),
                  bg=BG_COLOR, fg=ACCENT_COLOR)
header.place(relx=0.5, anchor="n")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=30, pady=70)

# ROM Tab
rom_tab = tk.Frame(notebook, bg=BG_COLOR); notebook.add(rom_tab, text="ROMs")
highlight_label = tk.Label(rom_tab, text="", fg=TEXT_COLOR, bg=BG_COLOR,
                           font=("Courier",12)); highlight_label.pack(pady=(0,10))
rom_var = tk.StringVar()
rom_dropdown = ttk.Combobox(rom_tab, textvariable=rom_var,
                            state="readonly", width=70); rom_dropdown.pack(pady=5)
tk.Button(rom_tab, text="▶ Play", command=play_selected,
          font=("Arial",14,"bold"), bg=ACCENT_COLOR, fg=BG_COLOR).pack(pady=8)
tk.Button(rom_tab, text="🔄 Refresh", command=refresh_rom_list,
          font=("Arial",12), bg=SECONDARY_COLOR, fg=BG_COLOR).pack(pady=4)
search_var = tk.StringVar(); search_var.trace_add("write", on_search)
tk.Entry(rom_tab, textvariable=search_var, font=("Courier",12), width=50,
         bg="#111122", fg=ACCENT_COLOR, insertbackground=ACCENT_COLOR).pack(pady=(10,10))
cover_frame_container = tk.Frame(rom_tab, bg=BG_COLOR); cover_frame_container.pack(fill="both", expand=True, padx=10, pady=10)
canvas = tk.Canvas(cover_frame_container, bg=BG_COLOR, highlightthickness=0)
scrollbar = ttk.Scrollbar(cover_frame_container, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)
cover_frame = tk.Frame(canvas, bg=BG_COLOR)
canvas.create_window((0,0), window=cover_frame, anchor="nw")
cover_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta/120),"units"))
rom_tab.bind("<Return>", lambda e: play_selected())

# Achievements Tab
ach_tab = tk.Frame(notebook, bg=BG_COLOR); notebook.add(ach_tab, text="Achievements")
ach_scroll_canvas = tk.Canvas(ach_tab, bg=BG_COLOR, highlightthickness=0)
ach_scroll_canvas.pack(side="left", fill="both", expand=True)
ach_scrollbar = ttk.Scrollbar(ach_tab, orient="vertical", command=ach_scroll_canvas.yview)
ach_scrollbar.pack(side="right", fill="y")
ach_scroll_canvas.configure(yscrollcommand=ach_scrollbar.set)

ach_tab_frame = tk.Frame(ach_scroll_canvas, bg=BG_COLOR)
ach_scroll_canvas.create_window((0, 0), window=ach_tab_frame, anchor="nw")
ach_tab_frame.bind("<Configure>", lambda e: ach_scroll_canvas.configure(scrollregion=ach_scroll_canvas.bbox("all")))

# System Output
print("\n📂 Available ROMs:")
for rom in get_rom_files():
    print(f"  - {rom}")

# Init
create_starfield()
animate_starfield()
animate_header()
notebook.bind("<<NotebookTabChanged>>", lambda e: populate_achievements_tab())
load_achievements()
check_and_unlock_achievements()
splash_boot()
refresh_rom_list()
root.mainloop()
