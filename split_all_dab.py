import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm

# --- Load config ---
with open("config.json", "r") as f:
    config = json.load(f)

game_path = config["game_path"]

# --- Validate EXE ---
if game_path.lower().endswith(".exe"):
    exe_name = os.path.basename(game_path).lower()

    if exe_name != "guilongchao.exe":
        print(f"[!] Invalid EXE: {exe_name}")
        print("[!] This script only supports GuiLongchao.exe")
        exit()

    root = os.path.dirname(game_path)
else:
    print("[!] Please provide path to GuiLongchao.exe in config.json")
    exit()

# --- Folder picker ---
root_tk = tk.Tk()
root_tk.withdraw()

output_base = filedialog.askdirectory(title="Select output folder")

if not output_base:
    print("[!] No output folder selected.")
    exit()

# --- Target folders ---
data_folder = os.path.join(root, "GuiLongchao_Data")

targets = [
    os.path.join(data_folder, "StreamingAssets", "Assetbundle"),
    os.path.join(data_folder, "PersistentPath", "Patch", "Assetbundle")
]

signature = b"UnityFS"

def split_dab(file_path):
    with open(file_path, "rb") as f:
        data = f.read()

    offsets = []
    i = 0

    while True:
        i = data.find(signature, i)
        if i == -1:
            break

        version_check = data[i+7:i+20]
        if any(c in version_check for c in b"0123456789."):
            offsets.append(i)

        i += 1

    if not offsets:
        print(f"[-] No bundles found in {file_path}")
        return

    offsets.append(len(data))

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    out_dir = os.path.join(output_base, base_name + "_split")
    os.makedirs(out_dir, exist_ok=True)

    # Progress bar for bundles
    for idx in tqdm(range(len(offsets) - 1),
                    desc=f"Splitting {base_name}",
                    leave=False):
        start = offsets[idx]
        end = offsets[idx + 1]

        chunk = data[start:end]

        out_file = os.path.join(out_dir, f"{base_name}_{idx:03}.ab")

        with open(out_file, "wb") as out:
            out.write(chunk)

# --- Collect all .dab files first ---
dab_files = []

for folder in targets:
    if not os.path.exists(folder):
        print(f"[!] Skipping missing folder: {folder}")
        continue

    for file in os.listdir(folder):
        full_path = os.path.join(folder, file)

        if not os.path.isfile(full_path):
            continue

        if file.lower().endswith(".bin"):
            continue

        if file.lower().endswith(".dab"):
            dab_files.append(full_path)

# --- Global progress bar ---
for file_path in tqdm(dab_files, desc="Processing .dab files"):
    split_dab(file_path)

print("Done!")
messagebox.showinfo("Finished", "All bundles have been extracted!")