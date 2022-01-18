import json
import re
import subprocess
import os
from static.constants import LOGO, KEYMAPS
from glob import glob

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
config = {}


def diskpart():
    r_expr_true = re.compile("^(yes|y)$")
    r_expr_false = re.compile("^(no|n)$")
    r_exp = re.compile("^[0-9]+")
    res = None
    disks = [
        "/dev/" + os.path.basename(os.path.dirname(d))
        for d in glob("/sys/block/*/device")
    ]
    print(
        """
------------------------------------------------------------------------
    THIS WILL FORMAT AND DELETE ALL DATA ON THE DISK             
    Please make sure you know what you are doing because         
    after formating your disk there is no way to get data back      
------------------------------------------------------------------------"""
    )
    print("Disks founded:")
    for i in range(len(disks)):
        print(f"{i+1}) {disks[i]}")
    while res is None:
        disk = input("Please enter disk: (example 1): ")
        res = r_exp.match(disk)
        if res is not None and 0 <= (int(disk) - 1) < len(disks):
            config["disk"] = disks[int(disk) - 1]
        else:
            res = None
    ssd = input("Is an SSD? (y/n) ").lower().strip()
    if r_expr_true.match(ssd) is not None:
        config["ssd"] = "yes"
    elif r_expr_false.match(ssd) is not None:
        config["ssd"] = "no"
    else:
        config["ssd"] = "no"


def filesystem():
    options = {1: "btrfs", 2: "ext4", 0: "exit"}
    r_exp = re.compile("^[0-9]+")
    print("Please select your filesystem for both boot and root")
    for (k, v) in options.items():
        print(f"{k}) {v}")
    selection = input("Insert the option number (default 1): ")
    res = r_exp.match(selection)
    if res is None or int(res.group()) not in options.keys():
        config["filesystem"] = options[1]
    elif int(res.group()) == 0:
        exit()
    else:
        config["filesystem"] = options[int(res.group())]


def timezone():
    r_expr_true = re.compile("^(yes|y)$")
    r_expr_false = re.compile("^(no|n)$")
    timezone = subprocess.run(
        "curl --fail https://ipapi.co/timezone".split(), capture_output=True, text=True
    )
    print(f"System detected your timezone to be {timezone.stdout}")
    answer = input("Is this correct? yes/no:").lower().strip()
    if r_expr_true.match(answer) is not None:
        config["timezone"] = timezone.stdout
    elif r_expr_false.match(answer) is not None:
        timezone = input("Please enter your desired timezone e.g. Europe/London: ")
        config["timezone"] = timezone
    else:
        config["timezone"] = timezone.stdout


def keymap():
    pass

if __name__ == "__main__":
    os.system("clear")
    print(LOGO)
    diskpart()
    os.system("clear")
    print(LOGO)
    filesystem()
    os.system("clear")
    print(LOGO)
    timezone()
    os.system("clear")
    keymap()
    with open(f"{SCRIPT_DIR}/config.json", "w") as out:
        json.dump(config, out, indent=2)
