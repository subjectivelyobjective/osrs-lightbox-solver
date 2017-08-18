#!/usr/bin/env python3
#
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

import argparse
import lightbox

def main():
    parser = argparse.ArgumentParser(description=("Solves Oldschool Runescape "
        "Lightbox puzzles through image recognition."))
    parser.parse_args()

    lb = lightbox.LightBox()
    solution = lightbox.solve(lb)
    solution_spaced = ""
    for switch in solution:
        solution_spaced += switch
        if switch != solution[-1]:
            solution_spaced += " "
    if solution is None:
        print("No solution was found. This shouldn't be possible. Try again.")
    else:
        print("Click the following switches in this order: " +
            solution_spaced + ".")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
