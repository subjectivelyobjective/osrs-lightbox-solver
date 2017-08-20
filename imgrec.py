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

import cv2
import lightbox
import math
import numpy as np
import os
import pathlib
import pyscreenshot as pys
import time
from operator import itemgetter
from pymouse import PyMouse
from pymouse import PyMouseEvent

threshold = 0.8
img_dir = os.path.join(str(pathlib.Path(__file__).parent), "images")
templ_switch_box = cv2.imread(os.path.join(img_dir, "switch-box.png"), 0)
templ_on = cv2.imread(os.path.join(img_dir, "lightbulb-on.png"), 0)
templ_off = cv2.imread(os.path.join(img_dir, "lightbulb-off.png"), 0)

w_sw = 67
h_sw = 30
w_gap = 9
h_gap = 37

class ImgRecException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class LatencyException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class LightboxClosedException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class PrematureSolveException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class UserMistakeException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

# Hackity hack hack.
class ImgRecFinishedInterrupt(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

def find_locs(img_gray_on):
    img_gray_off = img_gray_on.copy()
    res_on = cv2.matchTemplate(img_gray_on, templ_on, cv2.TM_CCOEFF_NORMED)
    res_off = cv2.matchTemplate(img_gray_off, templ_off, cv2.TM_CCOEFF_NORMED)
    loc_on = np.where(res_on >= threshold)
    loc_off = np.where(res_off >= threshold)
    locs = {"on": list(zip(*loc_on[::-1])), "off": list(zip(*loc_off[::-1]))}
    return locs

def top_row_find_sweep(locs):
    empty_on_row = False
    empty_off_row = False
    try:
        tp_on = min(locs["on"], key=itemgetter(1))
        empty_on_row = False
    except ValueError:
        empty_on_row = True
    try:
        tp_off = min(locs["off"], key=itemgetter(1))
        empty_off_row = False
    except ValueError:
        empty_off_row = True

    if empty_on_row:
        top_row_pos = tp_off[1]
    elif empty_off_row:
        top_row_pos = tp_on[1]
    else:
        top_row_pos = tp_on[1] if tp_on[1] <= tp_off[1] else tp_off[1]

    tp_on_locs = list(filter(lambda lb: lb[1] == top_row_pos, locs["on"]))
    tp_off_locs = list(filter(lambda lb: lb[1] == top_row_pos, locs["off"]))

    tp_row = tp_on_locs
    tp_row.extend(tp_off_locs)
    tp_row = sorted(tp_row, key=itemgetter(0))
    tp_row = list(map(lambda lb: 0 if lb in tp_off_locs else 1, tp_row))

    locs["on"] = list(filter(lambda loc: loc not in tp_on_locs, locs["on"]))
    locs["off"] = list(filter(lambda loc: loc not in tp_off_locs, locs["off"]))

    return (tp_row, locs)

def locs_to_state(lb, locs):
    lightbox_len = int(math.sqrt(len(locs["on"]) + len(locs["off"])))
    if lightbox_len != lb.length:
        raise ImgRecException("We expected " + str(lb.length) + " lightbulbs "
            + "in each row, but we only recognized "
            + str(lightbox_len) + " lightbulbs in each row.")

    state = []
    for row in range(0, lb.length):
        top_row, locs = top_row_find_sweep(locs)
        state.append(top_row)
    return state

def grab_screen_gray():
    pil_screen = pys.grab()
    return cv2.cvtColor(np.array(pil_screen), cv2.COLOR_RGB2GRAY)

def get_state(lb):
    img = grab_screen_gray()
    locs = find_locs(img)
    state = locs_to_state(lb, locs)
    return state

def find_switch_box():
    img_gray = grab_screen_gray()
    res = cv2.matchTemplate(img_gray, templ_switch_box, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    return list(zip(*loc[::-1]))

def in_switch_space(switch_spaces, pt):
    for switch in switch_spaces:
        tl_coord = switch_spaces[switch]
        x_check = (tl_coord[0] < pt[0]) and (pt[0] < tl_coord[0] + w_sw)
        y_check = (tl_coord[1] < pt[1]) and (pt[1] < tl_coord[1] + h_sw)
        in_sw_sp = x_check and y_check
        if in_sw_sp:
            return switch
    return None

def find_switch_spaces(lb):
    img_gray = grab_screen_gray()
    res = cv2.matchTemplate(img_gray, templ_switch_box, cv2.TM_CCOEFF_NORMED)
    locs = np.where(res >= threshold)
    try:
        tl_pt_a = list(zip(*locs[::-1]))[0]
    except IndexError:
        raise LightboxClosedException()
    tl_pt_e = (tl_pt_a[0], tl_pt_a[1] + h_gap)

    switches = lb.switches
    half_num_switches = lb.num_switches // 2    # Assumes that the switches are
                                                # in two rows
    switch_spaces = {i: (0,0) for i in lb.switches}
    for i in range(0, half_num_switches):
        tl_pt = tl_pt_a[0] + (w_sw * i) + (w_gap * i)
        switch_spaces[lb.switches[i]] = (tl_pt, tl_pt_a[1])

    j = 0
    for i in range(half_num_switches, lb.num_switches):
        tl_pt = tl_pt_e[0] + (w_sw * j) + (w_gap * j)
        switch_spaces[switches[i]] = (tl_pt, tl_pt_e[1])
        j += 1

    return switch_spaces

def lb_open():
    img_gray = grab_screen_gray()
    res = cv2.matchTemplate(img_gray, templ_switch_box, cv2.TM_CCOEFF_NORMED)
    locs = np.where(res >= threshold)
    return len(locs[0]) == 1

def switch_state_container(lb, initial_state=None):
    container = {}
    if initial_state is None:
        container["initial_state"] = []
    else:
        container["initial_state"] = initial_state
    container["switch_states"] = {}
    for switch in lb.switches:
        container["switch_states"][switch] = []
    return container

class SwitchStateGetter(PyMouseEvent):
    def __init__(self, lb, init_state):
        PyMouseEvent.__init__(self)
        self.lb = lb
        self.init_state = init_state
        self.switch_container = switch_state_container(lb, init_state)
        self.last_state = init_state
        self.curr_switch = ""
        self.completed = False

    def click(self, x, y, button, press):
        # Ignore mouse activity that isn't the mouse's left button release.
        if press or button != 1:
            return

        switch_spaces = find_switch_spaces(self.lb)
        switch_clicked = in_switch_space(switch_spaces, (x, y))
        if switch_clicked is None: # Ignore clicks that aren't on a switch.
            return

        # This is to account for the delay between switch click and lightbulb
        # change.
        time.sleep(0.5)

        for switch in self.switch_container["switch_states"]:
            if self.switch_container["switch_states"][switch] != []:
                continue
            self.curr_switch = switch
            break
        if self.curr_switch != switch_clicked:
            raise UserMistakeException("You were supposed to click switch " +
                self.curr_switch + ", but you clicked switch " +
                switch_clicked + ".")

        state = get_state(self.lb)
        if state == self.last_state:
            raise LatencyException()
        if state == self.lb.states["solved_state"]:
            raise PrematureSolveException()
        self.switch_container["switch_states"][self.curr_switch] = state
        self.last_state = state
        if self.curr_switch == self.lb.switches[-1]:
            self.completed = True
            raise ImgRecFinishedInterrupt()
        else:
            curr_switch_idx = self.lb.switches.index(self.curr_switch)
            next_sw = self.lb.switches[curr_switch_idx + 1]
            print("Now click switch " + next_sw + ".")

def rec_states(lb):
    waiting_for_lb = False
    wait_counter = 0
    while not lb_open():
        if not waiting_for_lb:
            waiting_for_lb = True
            print("Please open the Lightbox.")
            print("I'll wait.", end="")
        if wait_counter >= 200:
            print()
            print(("You left me waiting for longer than 5 minutes. I'll "
                "assume that you don't need me anymore."))
            exit(0)
        time.sleep(1.5)
        print(".", end="")
        wait_counter += 1
    if waiting_for_lb:
        # We don't need to set it back to False but let's do it anyway.
        waiting_for_lb = False
        print()
    init_state = get_state(lb)
    if (init_state == lb.states["solved_state"]):
        # We don't have to do anything because the lighrbox is already solved.
        print("The lightbox is solved!")
        exit(0)
    print("Found Lightbox! I'll now tell you to click the switches.")
    print("Don't click any switch besides the one I last told you to click.")
    print("If you mess up, close me with Ctrl-C twice and start me again.")
    print()
    print("Begin by clicking switch A.")
    swg = SwitchStateGetter(lb, init_state)
    try:
        swg.run()
    except ImgRecFinishedInterrupt:
        if swg.completed:
            return swg.switch_container
        else:
            return None
