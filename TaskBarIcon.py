# -*- coding: utf-8 -*-
"""
wxPomodoro - Simple pomodoro timer based on wxPython Phoenix GUI

The MIT License (MIT)
Copyright (C) 2017 Georgy Komarov <jubnzv@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""

import wx
import wx.adv


class TimerTaskBarIcon(wx.adv.TaskBarIcon):
    """Represents a icon located in task bar

    It also shows a current timer status.
    """

    def __init__(self, frame):
        super(TimerTaskBarIcon, self).__init__()

        self.frame = frame

        icon = wx.Icon('./icon.xpm')
        self.SetIcon(icon, "Test")
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.OnTaskBarLeftClick)

    def OnTaskBarLeftClick(self, event):
        """Create right-click menu"""
        self.frame.Show()
        self.frame.Restore()

    def OnTaskBarClose(self, event):
        """Destroy parent frame and taskbar itself"""
        self.frame.Close()

    def OnTaskBarActivate(self, event):
        pass
