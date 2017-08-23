# Copyright 2017 subjectivelyobjective.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# A complete and utter hackjob to make sure that "python setup.py install"
# does what it is supposed to do on both Windows and *nix. There has to be
# a better way to do this...

import os
import pip
import platform
import subprocess
import sys
import urllib.request as request
from setuptools import setup
from setuptools.command.install import install

manual_install_modules = {
    "cv2": ["cv2", "opencv-python"],
    "PIL": ["PIL", "Pillow-4.2.1"],
    "pyHook": ["pyHook", "pyHook-1.5.1"],
	"pynput": ["pynput", "pynput"],
    "pyscreenshot": ["pyscreenshot", "pyscreenshot"],
}

manual_repo = ("https://github.com/subjectivelyobjective/wheels/raw/master/"
    "wheels/")

class HandleModulesInWindows(install):
    def install_manually(self, mod):
        if not sys.platform.startswith("win32"):
            return
        try:
            exec("import " + manual_install_modules[mod][0])
        except ImportError:
            if mod == "cv2":
                # opencv-python installs with pip just fine, but does not when
                # simply listed in install_requires
                pip.main(["install", "--user", "opencv-python"])
                return
            if mod == "pynput":
                # Same story...
                pip.main(["install", "--user", "pynput"])
                return
            if mod == "pypiwin32":
                pip.main(["install", "--user", "pypiwin32"])
                return
            if mod == "pyscreenshot":
                pip.main(["install", "--user", "pyscreenshot"])
                return
            full_name = manual_install_modules[mod][1]
            url = manual_repo + "windows/"
            ver_num = str(sys.version_info[0]) + str(sys.version_info[1])
            if platform.architecture()[0] == "32bit":
                arch = "win32"
            elif platform.architecture()[0] == "64bit":
                arch = "win_amd64"
            whl = (full_name + "-cp" + ver_num + "-cp" + ver_num + "m-" + arch
                + ".whl")
            url += whl
            dest = os.path.expanduser("~/.lightbox-solver/wheels/windows")
            if not os.path.exists(dest):
                os.makedirs(dest)
            dest = os.path.join(dest, whl)
            if not os.path.exists(dest):
                print("Downloading: " + whl)
                with request.urlopen(url) as res, open(dest, "wb") as out:
                    buf = res.read()
                    out.write(buf)

            cmd = "pip install --user " + dest
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            for line in proc.stdout.readlines():
                print(line.decode())
            proc.wait()

    def run(self):
        if sys.platform.startswith("linux"):
            cmd = "which scrot"
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)
            proc.wait()
            if proc.returncode != 0:
                print("Did not find scrot! You might have to install it "
                    "yourself to satisfy pyscreenshot.")
        if not sys.platform.startswith("win32"):
            # We defer to pip for *nix platforms because it actually works on
            # them.
            print("This can take a while.")
            pip.main(["install", "--user", "."])
            return
        for mod in manual_install_modules:
            self.install_manually(mod)

setup(
   name="osrs-lightbox-solver",
   version="0.2.0",
   description="A script to solve Lightbox puzzles in Oldschool Runescape.",
   author="subjectivelyobjective",
   install_requires=["opencv-python", "pillow", "pynput",  "pyscreenshot",
        "pyuserinput",],
   cmdclass={"install": HandleModulesInWindows}
)
