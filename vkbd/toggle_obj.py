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

import dbus
import e_dbus
import dbus.service
import ecore

'''  Dbus  Object  '''
class DBusObject(dbus.service.Object):
    def __init__(self, ee, conn, object_path):
        dbus.service.Object.__init__(self, conn, object_path)
        self.ee = ee
        self.state = 1

    @dbus.service.signal("com.vkbd.Toggle",
                         signature='b')
    def ToggleSignal(self, b):
        # The signal is emitted when this method exits
        # You can have code here if you wish
        pass

    @dbus.service.method("com.vkbd.Toggle")
    def Show(self):
        self.ee.show()
        self.ToggleSignal(True)    
        return "Vkbd show"
        
    @dbus.service.method("com.vkbd.Toggle")
    def Hide(self):
        self.ee.hide()
        self.ToggleSignal(False)       
        return "Vkbd hide"
        
    @dbus.service.method("com.vkbd.Toggle",
                         out_signature="b")
    def GetState(self):       
        return self.ee.visibility_get()

    @dbus.service.method("com.vkbd.Toggle",
                         in_signature="", out_signature="")
    def Exit(self):
        ecore.idler_add(ecore.main_loop_quit)

class VkbdToggle():
    def __init__(self, ee):
        dbus_ml = e_dbus.DBusEcoreMainLoop()
        session_bus = dbus.SessionBus(mainloop=dbus_ml)

        session_bus.add_signal_receiver(self.__focus_in,
                signal_name='FocusIn',
                dbus_interface='org.ibus.panel')
        session_bus.add_signal_receiver(self.__focus_out,
                signal_name='FocusOut',
                dbus_interface='org.ibus.panel')

        name = dbus.service.BusName("com.vkbd.Toggle", session_bus)
        self.__dbus_obj = DBusObject(ee, name, "/com/vkbd/Toggle/toggle")


    def __focus_in(self, prop):
        print "Focus IN!"
        self.__dbus_obj.Show()

    def __focus_out(self, prop):
        print "Focus Out!"
        self.__dbus_obj.Hide()
