import string
import random
import winshell
import os
import subprocess
import sys
import re


# generate a random sequence of characters, default a-z A-Z
# numbers are optional but dangerous when used as the start of a variable name
def random_string(num, allow_uppercase=True, allow_numbers=False):
    pool = []
    pool.extend(string.ascii_lowercase)
    if allow_uppercase:
        pool.extend(string.ascii_uppercase)
    if allow_numbers:
        pool.extend([str(x) for x in range(0, 9)])

    output = ""
    for _ in range(num):
        output += random.choice(pool)
    return output


# creates shortcut with given parameters
def create_shortcut(lnk_file, target="", args="", title="title", icon=(), output_folder="."):

    if not lnk_file.endswith('.lnk'):
        lnk_file += ".lnk"

    f = os.path.join(output_folder, lnk_file)

    winshell.CreateShortcut(
        Path=f,
        Target=target,
        Icon=icon,
        Description=title,
        Arguments=args
    )


# lists all drives in the system
# TODO: linux
def get_drives():
    if 'win' in sys.platform:
        drivelist = subprocess.Popen('wmic logicaldisk get name,description', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        drivelisto, err = drivelist.communicate()
        return re.findall('[\s\t]([A-Z]\:)', str(drivelisto))
