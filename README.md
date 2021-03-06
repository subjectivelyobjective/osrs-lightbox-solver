osrs-lightbox-solver
====================

A Python 3 script that solves the Lightbox puzzle in Oldschool Runescape.

The script prompts the user to click the lightbox's switches alphabetically,
detects and keeps track of the lightbulb changes, uses the
information gathered to determine the solution, and gives it to the user for
them to enter.

## Requirements
 * Python 3.4 or newer
 * Pip 9 or newer

## Installation
```
$ python setup.py install
```

## Usage
 ```
$ python lightbox_solver.py
```

## Caveats
On Linux, you will probably have to install `scrot` with your distribution's
package manager.

Will not work under Wayland. For now use Xorg.

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
along with this program.  If not, see [here](http://www.gnu.org/licenses/).
