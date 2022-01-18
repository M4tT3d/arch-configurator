import sys
import os
from static.constants import LOGO
from glob import glob

SCRIPT_DIR = os.getcwd() + "/".join(sys.argv[0].split("/")[:-1])
if SCRIPT_DIR[1] == "/":
    SCRIPT_DIR = SCRIPT_DIR[1:]


def diskpart():
    disks = [
        "/dev/" + os.path.basename(os.path.dirname(d))
        for d in glob("/sys/block/*/device")
    ]
    for i in range(len(disks)):
        print(f"{i+1}) {disks[i]}")
    print(
        """
------------------------------------------------------------------------
    THIS WILL FORMAT AND DELETE ALL DATA ON THE DISK             
    Please make sure you know what you are doing because         
    after formating your disk there is no way to get data back      
------------------------------------------------------------------------"""
    )
    disk = input("Please enter full path to disk: (example /dev/sda): ")
    while disk not in disks:
        disk = input("Please enter full path to disk: (example /dev/sda): ")
    return disk


if __name__ == "__main__":
    print(LOGO)
    disk = diskpart()
    os.system("clear")
