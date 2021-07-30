#!/usr/bin/env python3
import argparse
from os import system, path, chdir, getcwd, environ, walk
import sys
import getpass
import subprocess
from zipfile import ZipFile

# KDE paths
kdePath = {
    "panel": ".config/plasma-org.kde.plasma.desktop-appletsrc",
    "globalTheme": [
        ".config/kdeglobals", ".config/kscreenlockerrc", ".config/kwinrc",
        ".config/gtkrc", ".config/gtkrc-2.0", ".config/gtk-4.0/",
        ".config/gtk-3.0/", ".config/gtk-2.0/", ".config/ksplashrc"
    ],
    "kvantum": ".config/Kvantum",
    "dolphin": ".config/dolphinrc",
    "kate": [
        ".config/katemetainfos", ".config/katerc", ".config/kateschemarc",
        ".config/katesyntaxhighlightingrc", ".config/katevirc"
    ],
    "kcalc": ".config/kcalcrc",
    "konsole": ".config/kconsolerc",
    "okular": [
        ".config/okular-generator-popplerrc",
        ".config/okularpartrc",
        ".config/okularrc",
    ],
    "userDir": ".config/user-dirs.dirs",
    "plasmaStyle": ".config/plasmarc",
    "colors": ".config/Trolltech.conf",
    "windowDecorations": ".config/kwinrulesrc",
    "fonts": ".config/kcmfonts",
    "cursors": ".config/kcminputrc",
    "fontManagement": ".config/kfontinstuirc",
    "shortcuts": [".config/kglobalshortcutsrc", ".config/khotkeysrc"],
    "backgroundServices": ".config/kded5rc",
    "desktopSession": ".config/ksmserverrc",
    "search": [".config/krunnerrc", ".config/baloofilerc"],
    "notifications": ".config/plasmanotifyrc",
    "regionalSettings": [".config/plasma-localerc", ".config/ktimezonedrc"],
    "accessibility": ".config/kaccessrc",
    "userFeedback": ".config/PlasmaUserFeedback",
    "layout": ".config/kxkbrc",
    "gamma": ".config/kgammarc",
    "energySaving": ".config/powermanagementprofilesrc"
}

for key in kdePath.keys():
    if isinstance(kdePath[key], list):
        for j in range(len(kdePath[key])):
            kdePath[key][j] = path.join(environ["HOME"], kdePath[key][j])
    else:
        kdePath[key] = path.join(environ["HOME"], kdePath[key])

parser = argparse.ArgumentParser(
    description=
    "utility to restore configuration on a new arch install. Files MUST have a package on every line",
    allow_abbrev=False)
group = parser.add_mutually_exclusive_group()
subparser = parser.add_subparsers(help="backup utility help")
backup = subparser.add_parser("backup")

group.add_argument("-i",
                   "--install",
                   metavar="<pkgFile>",
                   dest="pkgFile",
                   help="install packages from a file with pacman")
group.add_argument(
    "--installPikaur",
    metavar="<aurPkgFile>",
    dest="aurPkgFile",
    help=
    "install packages in file from aur with pikaur. If pikaur is not istalled, it will ask if it can be installed"
)
group.add_argument(
    "--base-system",
    metavar=("<pathInstall>", "<strapPkgFile>"),
    nargs=2,
    help="install all packages in strapPkgFile with pacstrap into pathInstall")
backup.add_argument("--pacman",
                    dest="pkgFileBack",
                    metavar="<pkgFile>",
                    help="create file with all packages installed from pacman")
backup.add_argument("--aur",
                    dest="aurPkgFileBack",
                    metavar="<aurPkgFile>",
                    help="create file with all packages installed from aur")
backup.add_argument("--kde",
                    metavar="file.zip",
                    const="kdeConfig.zip",
                    nargs="?",
                    help="create a backup of all kde config")
parser.add_argument("--restore-kde",
                    metavar="<file.zip>",
                    dest="backFile",
                    help="restore kde config files")
parser.add_argument("--base-config",
                    action="store_true",
                    help="set a base configuration on a new arch installation")

args, unknown = parser.parse_known_args()


def baseSystemInstall(pathInstall, pstrapPkgFile):
    if pathInstall[-1] == '/':
        pathInstall = pathInstall[:-1]
    command = "pacstrap " + pathInstall + " "
    with open(pstrapPkgFile) as file:
        for pkg in file:
            command += (pkg.strip() + " ")
        if input("Are you sure you want to continue? [y/N] ").lower() == "y":
            system(command)
            system(f"genfstab -U '{pathInstall}' >> '{pathInstall}'/etc/fstab")


def installPacman(pkgFile):
    with open(pkgFile) as pkgList:
        command = "pacman -S --needed "
        for pkg in pkgList:
            if "#" not in pkg:
                command += (pkg.strip() + " ")
        if (getpass.getuser() == "root"):
            system(command)
        else:
            exit("You need root permissions to do this")


def installPikaur(pkgFile):
    if not path.isfile("/usr/bin/pikaur"):
        choise = input("Do you want to install pikaur? [Y/n] ").strip().lower()
        if (choise != "y") and (choise != "n") and (choise != ''):
            exit("Input not valid")
        elif choise == "n":
            exit("Pikaur needed")
        oldCwd = getcwd()
        system("git clone https://aur.archlinux.org/pikaur.git")
        chdir("pikaur")
        system("makepkg -fsri")
        chdir(oldCwd)
        system("rm -r pikaur")
    with open(pkgFile) as pkgList:
        command = "pikaur -S --nodiff --noedit "
        for pkg in pkgList:
            if "#" not in pkg:
                command += (pkg.strip() + " ")
        if (getpass.getuser() != "root"):
            system(command)
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


def _zipdir(pathDir, ziph):
    # ziph is zipfile handle
    for root, dirs, files in walk(pathDir):
        for file in files:
            ziph.write(
                path.join(root, file),
                path.relpath(path.join(root, file), path.join(pathDir, '..')))


def backupKDE(zipPath):
    with ZipFile(zipPath, 'w') as zipF:
        for key in kdePath.keys():
            if isinstance(kdePath[key], list):
                for val in kdePath[key]:
                    if path.isdir(val):
                        _zipdir(val, zipF)
                    elif path.isfile(val):
                        zipF.write(
                            val,
                            path.relpath(val,
                                         path.join(path.split(val)[0], '.')))
            elif path.isdir(kdePath[key]):
                _zipdir(kdePath[key], zipF)
            elif path.isfile(kdePath[key]):
                zipF.write(
                    kdePath[key],
                    path.relpath(kdePath[key],
                                 path.join(path.split(kdePath[key])[0], '.')))

def baseConfiguration():
    if (getpass.getuser() == "root"):
        # set time zone
        zone = input("Insert time zone (ex Europe/Rome): ")
        system(f"ln -sf /usr/share/zoneinfo/{zone} /etc/localtime")
        system("hwclock --systohc")
        # set italian and english in locale.gen
        system("sed -i -e 's/#it_IT.UTF-8 UTF-8/it_IT.UTF-8 UTF-8/' /etc/locale.gen")
        system("sed -i -e 's/#en_GB.UTF-8 UTF-8/en_GB.UTF-8 UTF-8/' /etc/locale.gen")
        system('locale-gen')
        # set keymap in vconsole
        system("echo 'KEYMAP=it' > /etc/vconsole.conf")
        # set hostname
        hostname = input("Insert hostname: ")
        system(f"echo '{hostname}' > /etc/hostname")
        # create new user
        user = input("Insert user id: ")
        system(f"useradd -m -s /usr/bin/zsh {user}")
        system(f"passwd {user}")
        # root password
        print("Change root password")
        system("passwd root")
        # grub
        system("grub-install --target=x86_64-efi --efi-directory=/boot/efi/ --bootloader-id=GRUB")
        system("sed -i -e 's/#GRUB_THEME=\"/path/to/gfxtheme\"/GRUB_THEME=\"/usr/share/grub/themes/Vimix/theme.txt\"/' /etc/default/grub")
        system("grub-mkconfig -o /boot/grub/grub.cfg")
    else:
        exit("You need root permissions to do this")



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
        if args.kde is not None:
            backupKDE(args.kde)
    else:
        if args.base_system is not None:
            baseSystemInstall(args.base_system[0], args.base_system[1])
        if args.pkgFile is not None:
            installPacman(args.pkgFile)
        if args.aurPkgFile is not None:
            installPikaur(args.aurPkgFile)
        if args.backFile is not None:
            #TODO: function to restore kde settings
            pass
        if args.base_config:
            baseConfiguration()
