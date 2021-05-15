import argparse
from os import system, path, chdir, getcwd
import sys
import getpass
import subprocess

parser = argparse.ArgumentParser(
    description=
    "utility to restore configuration on a new arch install. Files MUST have a package on every line",
    allow_abbrev=False)
group = parser.add_mutually_exclusive_group()

group.add_argument("-i",
                   "--install",
                   metavar="<pkgFile>",
                   dest="pkgFile",
                   help="install packages from a file with pacman")
group.add_argument(
    "--pikaurInstall",
    metavar="<aurPkgFile>",
    dest="aurPkgFile",
    help=
    "install packages in file from aur with pikaur. If pikaur is not istalled, it will ask if it can be installed (default yes)"
)
group.add_argument(
    "--base-system",
    metavar=("<pathInstall>", "<strapPkgFile>"),
    nargs=2,
    help="install all packages in strapPkgFile with pacstrap into pathInstall")

subparser = parser.add_subparsers(help="backup utility help")
backup = subparser.add_parser("backup")
backup.add_argument("--pacman",
                    dest="pkgFileBack",
                    metavar="<pkgFile>",
                    help="create file with all packages installed from pacman")
backup.add_argument("--aur",
                    dest="aurPkgFileBack",
                    metavar="<aurPkgFile>",
                    help="create file with all packages installed from aur")
backup.add_argument("--kde",
                    action="store_true",
                    help="create a backup of all kde config")
backup.add_argument("--restore-kde", dest="", help="restore kde config files")

args, unknown = parser.parse_known_args()


def baseSystemInstall(pathInstall, pstrapPkgFile):
    command = "pacstrap " + pathInstall + " "
    with open(pstrapPkgFile) as file:
        for pkg in file:
            command += (pkg.strip() + " ")
        if input("Are you sure you want to continue? [y/N] ").lower() == "y":
            system(command)
            #print(command)


def installPacman(pkgFile):
    with open(pkgFile) as pkgList:
        command = "pacman -S --needed "
        for pkg in pkgList:
            command += (pkg.strip() + " ")
        if (getpass.getuser() == "root"):
            system(command)
            #print(command)
        else:
            exit("You need root permissions to do this")


def installPikaur(pkgFile):
    if not path.isfile("/usr/bin/pikaur"):
        flag = True
        choise = input("Do you want to install pikaur? [Y/n] ").strip().lower()
        if (choise != "y") and (choise != "n") and (choise != ''):
            exit("Input not valid")
        elif choise == "n":
            exit("Pikaur needed")
        if flag:
            oldCwd = getcwd()
            system("git clone https://aur.archlinux.org/pikaur.git")
            chdir("pikaur")
            system("makepkg -fsri")
            chdir(oldCwd)
            system("rm -r pikaur")
    with open(pkgFile) as pkgList:
        command = "pikaur -S --nodiff --noedit"
        for pkg in pkgList:
            command += (pkg.strip() + " ")
        if (getpass.getuser() != "root"):
            system(command)
            #print(command)
        else:
            exit("You not need root permissions to do this")


def backupPkgs(pkgFile, isPacman=True):
    with open(pkgFile, "w") as pkgList:
        if isPacman:
            proc = subprocess.run(
                'pacman -Qqe | grep -vx "$(pacman -Qqg base-devel)" | grep -vx "$(pacman -Qqm)"',
                shell=True,
                capture_output=True)
        else:
            proc = subprocess.run(["pacman", "-Qqm"], capture_output=True)
        pkgList.write(proc.stdout.decode("utf-8"))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)
        
    if len(unknown) > 0:
        parser.error("Unknown flag: " + " ".join(map(str, unknown)))
    if "pkgFileBack" in args:
        if args.pkgFileBack is not None:
            backupPkgs(args.pkgFileBack)
        if args.aurPkgFileBack is not None:
            backupPkgs(args.aurPkgFileBack, False)
        if args.kde:
            print("kde")
    else:
        if args.base_system is not None:
            baseSystemInstall(args.base_system[0], args.base_system[1])
        if args.pkgFile is not None:
            installPacman(args.pkgFile)
        if args.aurPkgFile is not None:
            installPikaur(args.aurPkgFile)