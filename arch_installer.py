from src.setupper.setupper import Setupper
import os
from static.constants import LOGO
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def info(str):
    line_length = 75
    print("-" * line_length)
    print(str)
    print("-" * line_length)


def prepare_install():
    info("\t\tSetting up mirrors for optimal download...")
    # update packages db
    os.system("pacman -Sy")
    # add parallel downloads
    os.system("sed -i 's/^#ParallelDownloads/ParallelDownloads/' /etc/pacman.conf")
    # install reflector
    os.system("pacman -S --noconfirm --needed reflector")
    # get country
    iso = subprocess.run(
        "curl -4 ifconfig.co/country-iso".split(), capture_output=True, text=True
    )
    info(f"\t\tSetting up {iso.stdout.strip()} mirrors for faster downloads")
    os.system(
        f"reflector -a 48 -c {iso} -f 5 -l 20 --sort rate --save /etc/pacman.d/mirrorlist"
    )
    info("\t\tFormatting Disk")



if __name__ == "__main__":
    conf = Setupper()
    conf.setupper()
    print(LOGO)
    prepare_install()
