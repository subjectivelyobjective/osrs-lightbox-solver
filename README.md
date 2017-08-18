osrs-lightbox-solver
====================

A Python 3 script to solve the Lightbox puzzle in Oldschool Runescape.

The script prompts the user to click the lightbox's switches alphabetically,
detects and keeps track of the lightbulb changes, uses the
information gathered to determine the solution, and gives it to the user for
them to enter.

## Requirements
 * python3

 ### From PyPI
 * opencv-python
 * pyscreenshot
 * pyuserinput

 ```
 $ pip3 install opencv-python pyscreenshot pyuserinput
 ```

 ### Windows-specific Requirements
 You will need Visual C++ redistributable 2015 from [here](https://www.microsoft.com/en-us/download/details.aspx?id=48145) if you
 do not already have it.

 ## Usage
 ```
usage: lightbox_solver.py [-h]

Solves Oldschool Runescape Lightbox puzzles through image recognition.

optional arguments:
  -h, --help  show this help message and exit
```

## Legalese
Copyright 2017 subjectivelyobjective.

"Oldschool Runescape" is Copyright 1999-2017 Jagex Ltd.
The images included in this program is Copyright 2017 Jagex Ltd.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see
<http://www.gnu.org/licenses/>.
