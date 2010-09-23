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

import sys
import os
import dbus
import e_dbus
import ecore

import ecore.evas
import ecore.x

import evas
import edje
import elementary

from ibus import Property

from gettext import dgettext
_  = lambda a : dgettext("ibus", a)
N_ = lambda a : a


def prop2string(prop):
    __prop_key = '/IBus/'+prop.get_key()
    __prop_label = prop.get_label().get_text()
    __prop_icon = prop.get_icon()
    __prop_tip = prop.get_tooltip().get_text()

    # workaround
    if len(__prop_icon)==0:
        # the setup icon
        if (prop.get_key()=='setup'):
            __prop_icon = 'configure'

    __prop = __prop_key + ':' + __prop_label + ':' + __prop_icon + ':' +  __prop_tip
    return __prop

class DbusPanel():
    def __init__(self, cand_panel):
        self.cand_panel = cand_panel
        dbus_ml = e_dbus.DBusEcoreMainLoop()
        bus = dbus.SessionBus(mainloop=dbus_ml)
        panel = bus.get_object("com.vkbd.panel",
                                object_path='/org/ibus/panel')
        self.panel_iface = dbus.Interface(panel, dbus_interface='org.ibus.panel')

        ##########callback of signal##############
        self.panel_iface.connect_to_signal("UpdateScreen", self.__update_screen)
        self.panel_iface.connect_to_signal("UpdateLookupTable", self.__update_lookup_table)
        self.panel_iface.connect_to_signal("ShowLookupTable", self.__lookup_table_set)
        #self.panel_iface.connect_to_signal("FocusIn", self.__focus_in)
        #self.panel_iface.connect_to_signal("FocusOut", self.__focus_out)
        self.panel_iface.connect_to_signal("StateChanged", self.__state_changed)
        self.panel_iface.connect_to_signal("UpdateProperty", self.__update_property)
        self.panel_iface.connect_to_signal("UpdatePreeditText", self.__update_preedit_text)
        self.panel_iface.connect_to_signal("UpdatePreeditCaret", self.__update_preedit_caret)
        self.panel_iface.connect_to_signal("ShowPreedit", self.__preedit_set)
        self.panel_iface.connect_to_signal("UpdateAux", self.__update_aux)
        self.panel_iface.connect_to_signal("ShowAux", self.__aux_set)

    def __update_lookup_table(self, labels,items,xs,bool1,bool2):
        print "hello!!"
        #for i in range(len(items)):
        #    print "items[%d]:" %i, "", 
        #    print items[i]
        self.cand_panel.cand_area.set_labels(items)

    def __lookup_table_set(self, b):
        if b:
            print "show LookupTable!"
            self.cand_panel.cand_area.show_items()
        else:
            print "hide LookupTable!"
            self.cand_panel.cand_area.hide_items()

    def __update_screen(self, b):
        print "Update screen!!"

    ###never focus in???
    ####some global method???
    #def __focus_in(self, prop):
    #    print "Focus in!"
        #self.cand_panel.vkbd.ee.show()
        #self.toggle_iface.Show()

    #def __focus_out(self, prop):
    #    print "Focus out!"
        #self.cand_panel.vkbd.ee.hide()
        #self.toggle_iface.Hide()

    def __state_changed(self, prop):
        print "State changed!!"
        #print prop
        if not ":" in prop:
            return
        part = prop.split(':')
        #print part[2]

        self.cand_panel.set_icon(part[2])

    def __update_property(self, prop):
        #print prop
        if not ":" in prop:
            return
        part = prop.split(':')
        #print part[2]

        #self.cand_panel.set_icon(part[2])

         ##what is preedit ??##
    def __preedit_set(self, b):
        print "preedit set!!"

    def __update_preedit_text(self, text, attr):
        print "update preedit text..."
        #print text, attr

        #self.cand_panel.preedit_label.part_text_set("label", text)

    def __update_preedit_caret(self, pos):
        print "update preedit caret!"

    def __update_aux(self, text, attr):
        print "update AUX!"
        self.cand_panel.preedit_label.part_text_set("label", text)

    def __aux_set(self, b):
        if b:
            print "show AUX!"
            self.cand_panel.preedit_label.show()
        else:
            print "hide AUX!"
            self.cand_panel.preedit_label.hide()

        #print b

    ########### DBus Call #################
    def page_up(self):
        self.panel_iface.PageUp()

    def page_down(self):
        self.panel_iface.PageDown()

    def candidate_clicked(self, index, button, state):
        self.panel_iface.CandidateClicked(index, button, state)

    def turn_off_input_method(self):
        prop = Property(key='Engine/None',label=_('Disable'))
        #print "turn off"
        #print prop2string(prop)
        self.panel_iface.VKBDTriggerProp(prop2string(prop))

    def turn_on_input_method(self):
        im_menu = self.panel_iface.Get_IM_Menu()
        #print im_menu[0]
        ####Turn on the first IM
        self.panel_iface.VKBDTriggerProp(im_menu[0])

    def __del__(self):
        self.turn_off_input_method()


class CandidateArea():
    def __init__(self, panel, canvas, edje_file):
        self.canvas = canvas
        self.edje_file = edje_file
        self.panel = panel
        self.__cand_item = []
        
        self.cand_area_edje = panel.panel_edje.part_swallow_get("cand_area")

    def creat_ui(self):
        for i in range(0, 8):
            o = edje.Edje(self.canvas)
            o.file_set(self.edje_file, "vkbd/cand_item")
            o.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)   #####
            o.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
            o.part_text_set("id", "%s" %(i+1))
#            o.part_text_set("label", itmes[i])
            o.signal_callback_add("id,clicked", "*",
                                   self.__id_clicked)
            o.signal_callback_add("label,clicked", "*",
                                    self.__label_clicked)
            self.__cand_item.append(o)
            self.cand_area_edje.part_box_append("hbox", o)
            o.show()


    def __id_clicked(self, edje_obj, emission, source, data=None):
        print "clicked ID"

    def __label_clicked(self, edje_obj, emission, source, data=None):
        id = edje_obj.part_text_get("id")
        #print "clicked %s" %label
        index = int(id) -1
        self.panel.dbus_panel.candidate_clicked(index, 1, 1)

    def set_labels(self, labels):
        if not labels:
            for i in xrange(0, 8):
                self.__cand_item[i].part_text_set("label", "")
            return

        i = 0
        for text in labels:
            self.__cand_item[i].part_text_set("label", text.encode('utf-8'))
            i += 1
            if i >= 8:
                break

    def show_items(self):
        for i in range(len(self.__cand_item)):
            self.__cand_item[i].show()

    def hide_items(self):
        for i in range(len(self.__cand_item)):
            self.__cand_item[i].hide()


class CandidatePanel():
    def __init__(self, canvas, edje_file):
        self.canvas = canvas
        self.edje_file = edje_file

        self.panel_edje = edje.Edje(canvas, file=edje_file, group="vkbd/cand_panel")
        self.cand_area = CandidateArea(self, self.canvas, self.edje_file)
        self.dbus_panel = DbusPanel(self)

        self.__creat_ui()
        
    def __creat_ui(self):
        self.cand_area.creat_ui()

        self.preedit_label = edje.Edje(self.canvas)
        self.preedit_label.file_set(self.edje_file, "vkbd/preedit_label")
        self.panel_edje.part_swallow("preedit_label", self.preedit_label)

        ic = edje.Edje(self.canvas)
        ic.file_set(self.edje_file, "icon/logo")
        self.logo_bt = elementary.Button(self.panel_edje)
        self.logo_bt.icon_set(ic)
        #bt.callback_clicked_add(self.append_item, items[i])
        self.panel_edje.part_swallow("input_logo", self.logo_bt)
        self.logo_bt.show()
        ic.show()
        
        ic = elementary.Icon(self.panel_edje)
        ic.file_set(self.edje_file, "icon/page_up")
        bt = elementary.Button(self.panel_edje)
        bt.icon_set(ic)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(0.0, 0.0)
        bt.callback_clicked_add(self.page_up)
        self.panel_edje.part_swallow("page_up", bt)
        #bt.show()
        #ic.show()

        ic = edje.Edje(self.canvas)
        ic.file_set(self.edje_file, "icon/page_down")
        ic.size_hint_aspect_set(evas.EVAS_ASPECT_CONTROL_VERTICAL, 1, 1)
        bt = elementary.Button(self.panel_edje)
        bt.icon_set(ic)
        bt.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        bt.size_hint_weight_set(0.0, 0.0)
        bt.callback_clicked_add(self.page_down)
        self.panel_edje.part_swallow("page_down", bt)
        #bt.show()
        #ic.show()
        

#        box.show()

    def page_up(self, obj, *args, **kwargs):
        self.dbus_panel.page_up()

    def page_down(self, obj, *args, **kwargs):
        self.dbus_panel.page_down()

    def set_icon(self, icon):
        ic = elementary.Icon(self.panel_edje)
        if os.path.isfile(icon):
            ic.file_set(icon)
        else:
            ic.file_set(self.edje_file, "icon/logo")
        self.logo_bt.icon_set(ic)

    def show_all(self):
        self.panel_edje.show()

    def hide_all(self):
        self.panel_edje.hide()

    def turn_off_input_method(self):
        self.dbus_panel.turn_off_input_method()

    def turn_on_input_method(self):
        self.dbus_panel.turn_on_input_method()

#######################################################################
def destroy(obj):
    elementary.exit()

def on_resize(ee):
    x, y, w, h = ee.evas.viewport
    ee.data["main"].size = w, h

if __name__ == "__main__":
    ee = ecore.evas.SoftwareX11(w=800, h=70)
    ex = ecore.x.Window_from_xid(ee.window_get())
    ex.icccm_hints_set(0, 1, 0, 0, 0, 0, 0)
    canvas = ee.evas

    panel = CandidatePanel(ee, canvas, "vkbd.edj")
    panel.panel_edje.size = canvas.size
    panel.panel_edje.show()

    ee.title = "Panel"
    ee.data["main"] = panel.panel_edje
    ee.callback_resize = on_resize
    ee.show()
    ex.show()

    ecore.main_loop_begin()
