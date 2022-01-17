import sys
import os
from static.constants import LOGO

SCRIPT_DIR = os.getcwd() + "/".join(sys.argv[0].split("/")[:-1])
if SCRIPT_DIR[0] == "/":
    SCRIPT_DIR = SCRIPT_DIR[1:]


if __name__ == "__main__":
    print(LOGO)
