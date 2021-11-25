MAX_BACKUP = 3

import psutil
from functools import reduce
import os
import time
from pathlib import Path
import shutil

mc_path = r"%LOCALAPPDATA%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds"
mc_dir = os.path.expandvars(mc_path)

save_dir = os.path.join(Path.home(), ".minecraft-backup")


def is_mc_running():
    return True in map(lambda p : "Minecraft" in psutil.Process(pid=p).name(), psutil.pids())

def get_worlds():
    def read_world_name(folder):
        with open(os.path.join(mc_dir, fr"{folder}\levelname.txt"), "r") as f:
            return f.read()

    return list(
        map(
            lambda f : (read_world_name(f), f),
            sorted([os.path.join(mc_dir, x) for x in os.listdir(mc_dir)], key=os.path.getmtime)
        )
    )[::-1]

def try_int(i):
    try:
        return int(i)
    except:
        return 0

def is_int(i):
    try:
        int(i)
        return True
    except:
        return False

def step(worlds):
    world_name, folder_name = worlds[0]
    out_dir = os.path.join(save_dir, world_name)
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    suffix_len = len(str(MAX_BACKUP))
    [shutil.rmtree(os.path.join(out_dir, x)) for x in filter(
            lambda s: try_int(s[-suffix_len:]) >= MAX_BACKUP,
            map(lambda f: [f[1], os.rename(os.path.join(out_dir, f[0]), os.path.join(out_dir, f[1]))][0],
                map(
                    lambda f: (f, (f"{f[:-suffix_len]}{int(f[-suffix_len:])+1}" if is_int(f[-suffix_len:]) else (f"{f}_%0{suffix_len}d") % 1)),
                    sorted(os.listdir(out_dir))[::-1]
                )
            )
        )
     ]

    shutil.copytree(folder_name, os.path.join(out_dir, os.path.basename(folder_name)))

def main():
    while time.sleep(900):
        if not is_mc_running():
            continue

        worlds = get_worlds()
        if len(worlds < 1):
            continue

        step(worlds)


if __name__ == "__main__":
    main()
