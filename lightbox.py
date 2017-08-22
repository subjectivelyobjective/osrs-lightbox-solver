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

import imgrec
import mathutil

# We assume that it is a square light box. In OSRS's case it is a 5x5 light
# box.
default_length = 5

# Number of switches in the light box. In OSRS's case it is 8.
default_num_switches = 8

def get_switch_states(lightbox):
    done = False
    while not done:
        states = imgrec.rec_states(lightbox)
        if states is None:
            print("Something went wrong and we're not sure why.")
            print("Let's try again.")
            print()
            continue
        elif issubclass(states.__class__, Exception):
            if states.__class__ == imgrec.ImgRecException:
                print("Failed to recognize all of the lightbulbs.")
            elif states.__class__ == imgrec.LatencyException:
                print(("We detected that you clicked a switch, but we didn't "
                    "detect any change in the lightbulbs."))
            elif states.__class__ == imgrec.LightboxClosedException:
                print("The lightbox was closed!")
                print(("If don't need a lightbox solved anymore, close me by "
                    "pressing Ctrl-C."))
            elif states.__class__ == imgrec.PrematureSolveException:
                print("The lightbox is solved!")
                exit(0)
            elif states.__class__ == imgrec.UserMistakeException:
                print(states)
            else:
                raise states
            print("You will have to start over again.")
            print()
            continue
        lightbox.states["initial_state"] = states["initial_state"]
        lightbox.states["switch_states"] = states["switch_states"]
        lightbox.states["current_state"] = states["switch_states"]["H"]
        done = True

def get_switch_behavior(lightbox):
    switch_behavior = {};
    prev_switch = lightbox.states["initial_state"]
    for switch in lightbox.switches:
        curr_switch = lightbox.states["switch_states"][switch]
        switch_behavior[switch] = mathutil.matrix_xor(prev_switch, curr_switch)
        prev_switch = curr_switch
    lightbox.switch_behavior = switch_behavior

# Makes a dict that matches switches with the lightbulbs that they
# toggle.
def make_switches(num_switches):
    switches = []
    START_CHAR = 65   # Start of uppercase ASCII chars, so "A"
    current_char = START_CHAR
    for START_CHAR in range(START_CHAR, START_CHAR + num_switches):
        switches.append(chr(current_char))
        current_char+=1
    return switches

def solve(lightbox):
    switches = lightbox.switches
    get_switch_states(lightbox)
    get_switch_behavior(lightbox)
    all_possible_solutions = mathutil.char_combinations("".join(switches))

    solution = ""
    for poss_sol in all_possible_solutions:
        matrix = lightbox.states["current_state"]
        for switch in list(poss_sol):
            matrix = mathutil.matrix_xor(matrix, lightbox.switch_behavior[switch])
        if matrix == lightbox.states["solved_state"]:
            solution = poss_sol # Solved!
            break

    if solution != "":
        return solution
    else:
        return None # Who knows what went wrong.

class LightBox:
    def __init__(self, num_switches=default_num_switches,
        length=default_length, states={}, switch_behavior={}):

        self.num_switches = num_switches
        self.switches = make_switches(self.num_switches)
        self.length = length
        self.states = states
        self.states["switch_states"] = {}
        self.states["current_state"] = []
        self.states["solved_state"] = mathutil.unit_matrix(self.length)
        self.switch_behavior = switch_behavior
