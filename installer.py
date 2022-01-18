from src.setupper.setupper import Setupper
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":
    conf = Setupper()
    conf.setupper()
    conf.save_setup(SCRIPT_DIR)
