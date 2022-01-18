from static.constants import LOGO, KEYMAPS
import re
import os
from glob import glob
import subprocess
import json


class Setupper:
    def __init__(
        self, disk=None, ssd="no", filesystem="btrfs", timezone=None, keymap="us"
    ):
        self._disk = disk
        self._ssd = ssd
        self._fs = filesystem
        self._tzone = timezone
        self._km = keymap

    # GETTERS
    def get_disk(self):
        return self._disk

    def get_fs(self):
        return self._fs

    def get_timezone(self):
        return self._tzone

    def get_keymap(self):
        return self._km

    def _diskpart(self):
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
                self._disk = disks[int(disk) - 1]
            else:
                res = None
        ssd = input("Is an SSD? (y/n) ").lower().strip()
        if r_expr_true.match(ssd) is not None:
            self._ssd = "yes"
        elif r_expr_false.match(ssd) is not None:
            self._ssd = "no"

    def _filesystem(self):
        options = {1: "btrfs", 2: "ext4", 0: "exit"}
        r_exp = re.compile("^[0-9]+")
        print("Please select your filesystem for both boot and root")
        for (k, v) in options.items():
            print(f"{k}) {v}")
        selection = input("Insert the option number (default 1): ")
        res = r_exp.match(selection)
        if res is None or int(res.group()) not in options.keys():
            self._fs = options[1]
        elif int(res.group()) == 0:
            exit()
        else:
            self._fs = options[int(res.group())]

    def _timezone(self):
        r_expr_true = re.compile("^(yes|y)$")
        r_expr_false = re.compile("^(no|n)$")
        timezone = subprocess.run(
            "curl --fail https://ipapi.co/timezone".split(),
            capture_output=True,
            text=True,
        )
        print(f"System detected your timezone to be {timezone.stdout}")
        answer = input("Is this correct? yes/no:").lower().strip()
        if r_expr_true.match(answer) is not None:
            self._tzone = timezone.stdout
        elif r_expr_false.match(answer) is not None:
            timezone = input("Please enter your desired timezone e.g. Europe/London: ")
            self._tzone = timezone
        else:
            self._tzone = timezone.stdout

    def _keymap(self):
        j = 0
        r_exp = re.compile(r"^[a-z]{2}$")
        for i in range(len(KEYMAPS)):
            print(f"{i + 1}) {KEYMAPS[i]}", end="\t\t")
            j += 1
            if j == 5:
                print()
                j = 0
        print()
        keymap = input("Choose keymap: ")
        while r_exp.match(keymap) is None:
            keymap = input("Choose keymap: ")
        self._km = keymap

    def setupper(self):
        os.system("clear")
        print(LOGO)
        self._diskpart()
        os.system("clear")
        print(LOGO)
        self._filesystem()
        os.system("clear")
        print(LOGO)
        self._timezone()
        os.system("clear")
        print(LOGO)
        self._keymap()
        os.system("clear")

    def save_setup(self, dir):
        config = {}
        config['disk'] = self._disk
        config['ssd'] = self._ssd
        config['filesystem'] = self._fs
        config['timezone'] = self._tzone
        config['keymap'] = self._km
        with open(f"{dir}/config.json", "w") as out:
            json.dump(config, out, indent=2)
