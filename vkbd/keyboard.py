#
# This file is part of vkbd-ng
# Copyright (C) 2010 mink365 <mink365@gmail.com>
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
# Additional permission under GNU GPL version 3 section 7
#
# The copyright holders grant you an additional permission under Section 7
# of the GNU General Public License, version 3, exempting you from the
# requirement in Section 6 of the GNU General Public License, version 3, to
# accompany Corresponding Source with Installation Information for the
# Program or any work based on the Program. You are still required to comply
# with all other Section 6 requirements to provide Corresponding Source.
#

import os
import sys
import virtkey
import edje
import edje.decorators
import evas
import evas.decorators

from gettext import dgettext
_  = lambda a : dgettext("ibus", a)
N_ = lambda a : a

''' virtkey '''
v = virtkey.virtkey()


#class ToggleButton(self, ):


class VirtualKeyboard(edje.Edje):
    def __init__(self, vkbd, canvas, edje_file):
        edje.Edje.__init__(self, canvas)
        self.text = []
        self.vkbd = vkbd
        self.file_set(edje_file, "vkbd/keyboard")
        self.obj = {
            "alpha": self.part_swallow_get("alpha"),
            "special-1": self.part_swallow_get("special-1"),
            "special-2": self.part_swallow_get("special-2"),
            }
        self.pressed_keys = {}
        self.is_shift_down = False
        self.is_mouse_down = False
        self.is_cn_down = False

	'''   Shift Toggle  '''
    def press_shift(self):
        self.obj["alpha"].signal_emit("press_shift", "")
        v.lock_mod(1)
        self.is_shift_down = True

    def release_shift(self):
        self.obj["alpha"].signal_emit("release_shift", "")
        v.unlock_mod(1)
        self.is_shift_down = False

    def toggle_shift(self):
        if self.is_shift_down:
            self.release_shift()
        else:
            self.press_shift()

	"""    CN Toggle    """            
    def press_cn(self):
        self.obj["alpha"].signal_emit("press_fcitx", "") #"" but "*"
        self.vkbd.vkbd_edje.signal_emit("show-cand_panel", "")
        self.vkbd.cand_panel.turn_on_input_method()
        self.is_cn_down = True

    def release_cn(self):
        self.obj["alpha"].signal_emit("release_fcitx", "")
        self.vkbd.vkbd_edje.signal_emit("hide-cand_panel", "")
        self.vkbd.cand_panel.turn_off_input_method()
        self.is_cn_down = False

    def toggle_cn(self):
        if self.is_cn_down:
            self.release_cn()
        else:
            self.press_cn()

    @edje.decorators.signal_callback("key_down", "*")
    def on_edje_signal_key_down(self, emission, source):
    	#print source
        if ':' in source:
            part, key = source.split(":", 1)
        else:
            key = source
        if key == "enter":
			v.press_keycode(36)
			v.release_keycode(36)
            #self.press_shift()
        elif key == "@":
			v.press_keysym(0x40)
			v.release_keysym(0x40)
        elif key == "backspace":
			v.press_keycode(22)
			v.release_keycode(22)
        elif key == "space":
			v.press_keycode(65)
			v.release_keycode(65) 
        elif key == "up":
			v.press_keycode(111)
			v.release_keycode(111)
        elif key == "tab":
			v.press_keycode(23)
			v.release_keycode(23)            
        elif key == "shift":
            self.toggle_shift()
        elif key == "fcitx":
            self.toggle_cn()
        elif key in (".?123", "ABC", "#+=", ".?12"):
            pass
        elif "0x" in key:
        	v.press_keysym(int(key, 16))
        	v.release_keysym(int(key, 16))
        else:
			v.press_keycode(int(key))
			v.release_keycode(int(key))

    @edje.decorators.signal_callback("mouse_over_key", "*")
    def on_edje_signal_mouse_over_key(self, emission, source):
        if not self.is_mouse_down:
            return
        if ':' not in source:
            return
        part, subpart = source.split(':', 1)
        o = self.obj[part]

        if subpart in self.pressed_keys:
            return

        for k in self.pressed_keys.values():
            o.signal_emit("release_key", k)
        self.pressed_keys.clear()
        self.pressed_keys[subpart] = subpart
        o.signal_emit("press_key", subpart)

    @edje.decorators.signal_callback("mouse_out_key", "*")
    def on_edje_signal_mouse_out_key(self, emission, source):
        if not self.is_mouse_down:
            return
        if ':' not in source:
            return
        part, subpart = source.split(':', 1)
        o = self.obj[part]

        if subpart in self.pressed_keys:
            del self.pressed_keys[subpart]
            o.signal_emit("release_key", subpart)


    @edje.decorators.signal_callback("mouse,down,1", "*")
    def on_edje_signal_mouse_down_key(self, emission, source):
        if ':' not in source:
            return
        part, subpart = source.split(':', 1)
        o = self.obj[part]
        self.is_mouse_down = True

        if subpart in self.pressed_keys:
            return

        for k in self.pressed_keys.values():
            o.signal_emit("release_key", k)
        self.pressed_keys.clear()
        self.pressed_keys[subpart] = subpart
        o.signal_emit("press_key", subpart)

    @edje.decorators.signal_callback("mouse,down,1,*", "*")
    def on_edje_signal_mouse_down_multiple_key(self, emission, source):
        self.on_edje_signal_mouse_down_key(self, emission, source)

    @edje.decorators.signal_callback("mouse,up,1", "*")
    def on_edje_signal_mouse_up_key(self, emission, source):
    	#print source
        if ':' not in source:
            return
        part, subpart = source.split(':', 1)
        o = self.obj[part]
        self.is_mouse_down = False
        if subpart in self.pressed_keys:
            del self.pressed_keys[subpart]
            o.signal_emit("release_key", subpart)
            o.signal_emit("activated_key", subpart)

    @evas.decorators.mouse_down_callback
    def on_mouse_down(self, event):
        if event.button != 1:
            return
        self.is_mouse_down = True

    @evas.decorators.mouse_up_callback
    def on_mouse_up(self, event):
        if event.button != 1:
            return
        self.is_mouse_down = False

    @evas.decorators.key_down_callback
    def on_key_down(self, event):
        k = event.keyname.lower()
        if k == "return":
            k = "enter"
        elif k == "backspace":
            pass
        elif k.startswith("shift"):
            k = "shift"
        elif k.startswith("alt_"):
            return
        elif k.startswith("control_"):
            return
        else:
            k = event.string

        if k:
            o.signal_emit("key_down", k)


