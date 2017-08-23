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
import sys
import threading
import time
from queue import Queue
from pynput import mouse

if not sys.platform.startswith("win32"):
    # Work around to make Windows stop importing PyUserInput, which it chokes
    # on during the installation process.
    exec("from pymouse import PyMouse")
    exec("from pymouse import PyMouseEvent")

def win_queueing(win_swg):
    while not win_swg.completed:
        func, args, kwargs = win_swg.queue.get()
        func(*args, **kwargs)
        win_swg.queue.task_done()
    win_swg.listener.stop()

class SwitchStateGetterNix(PyMouseEvent):
    def __init__(self, lb, init_state):
        PyMouseEvent.__init__(self)
        self.lb = lb
        self.init_state = init_state
        self.switch_container = imgrec.switch_state_container(lb, init_state)
        self.last_state = init_state
        self.curr_switch = ""
        self.completed = False
        self.exception = None

    def click(self, x, y, button, press):
        # Ignore mouse activity that isn't the mouse's left button release.
        if press or button != 1:
            return

        switch_spaces = imgrec.find_switch_spaces(self.lb)
        if switch_spaces == -1:
            self.exception = imgrec.LightboxClosedException()
            raise self.exception
        switch_clicked = imgrec.in_switch_space(switch_spaces, (x, y))
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
            self.exception = imgrec.UserMistakeException("You were supposed to " +
                "click switch " + self.curr_switch + ", but you clicked " +
                "switch " + switch_clicked + ".")
            raise self.exception

        state = imgrec.get_state(self.lb)
        if state == self.last_state:
            self.exception = imgrec.LatencyException()
            raise self.exception
        if state == self.lb.states["solved_state"]:
            self.exception = imgrec.PrematureSolveException()
            raise self.exception
        self.switch_container["switch_states"][self.curr_switch] = state
        self.last_state = state
        if self.curr_switch == self.lb.switches[-1]:
            self.completed = True
            raise imgrec.ImgRecFinishedInterrupt()
        else:
            curr_switch_idx = self.lb.switches.index(self.curr_switch)
            next_sw = self.lb.switches[curr_switch_idx + 1]
            print("Now click switch " + next_sw + ".")

class SwitchStateGetterWin:
    def __init__(self, lb, init_state):
        self.lb = lb
        self.init_state = init_state
        self.switch_container = imgrec.switch_state_container(lb, init_state)
        self.last_state = init_state
        self.curr_switch = ""
        self.completed = False
        self.exception = None
        self.listener = None
        self.queue = Queue()
        self.helper = threading.Thread(target=win_queueing, args=(self,))

    def handle_click(self, x, y):
        switch_spaces = imgrec.find_switch_spaces(self.lb)
        if switch_spaces == -1:
            self.exception = imgrec.LightboxClosedException()
            self.completed = True
            return
        switch_clicked = imgrec.in_switch_space(switch_spaces, (x, y))
        if switch_clicked is None: # Ignore clicks that aren't on a switch.
            return

        switch_spaces = imgrec.find_switch_spaces(self.lb)
        switch_clicked = imgrec.in_switch_space(switch_spaces, (x, y))
        if switch_clicked is None: # Ignore clicks that aren't on a switch.
            return

        for switch in self.switch_container["switch_states"]:
            if self.switch_container["switch_states"][switch] != []:
                continue
            self.curr_switch = switch
            break
        if self.curr_switch != switch_clicked:
            self.exception = imgrec.UserMistakeException("You were supposed to " +
                "click switch " + self.curr_switch + ", but you clicked " +
                "switch " + switch_clicked + ".")
            self.completed = True

        state = imgrec.get_state(self.lb)
        if state == self.last_state:
            self.exception = imgrec.LatencyException()
            self.completed = True
            return
        if state == self.lb.states["solved_state"]:
            self.exception = imgrec.PrematureSolveException()
            self.completed = True
            return
        self.switch_container["switch_states"][self.curr_switch] = state
        self.last_state = state
        if self.curr_switch == self.lb.switches[-1]:
            self.completed = True
        else:
            curr_switch_idx = self.lb.switches.index(self.curr_switch)
            next_sw = self.lb.switches[curr_switch_idx + 1]
            print("Now click switch " + next_sw + ".")
            return

    def on_click(self, x, y, button, pressed):
        if pressed or button != mouse.Button.left:
            return
        self.queue.put((self.handle_click, (x, y), {}))

    def run(self):
        self.helper.start()
        with mouse.Listener(on_click=self.on_click) as listener:
            self.listener = listener
            self.listener.join()
