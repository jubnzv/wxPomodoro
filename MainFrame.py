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
import datetime
import time

from TaskBarIcon import TimerTaskBarIcon


class MainFrame(wx.Frame):
    """Main frame of program
    """

    TIME_UNITS = ['sec', 'min', 'hour']

    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)

        # Timer values
        self.STATUS = 'Stopped'
        self.t_remain = self.t_start = self.t_stop = self.t_tick = datetime.timedelta()

        # Initialize the timer
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.TimerLoop)

        # Intiailize the UI
        self.mainPanel = wx.Panel(self)
        self.mainSz = wx.BoxSizer(wx.VERTICAL)
        self._initStatusPanel()
        self._initTimerPanel()
        self._initControlButtons()
        self._initTrayIcon()
        self._setTitle()
        self.mainSz.Fit(self)
        self.mainPanel.SetSizer(self.mainSz)

    def _initStatusPanel(self):
        """Initialize the status panel that represents current pomodoro state"""
        statusPanel = wx.StaticBox(self.mainPanel, wx.ID_ANY, label='Current pomodoro')
        statusSz = wx.StaticBoxSizer(statusPanel, wx.HORIZONTAL)

        self.currentTime = wx.TextCtrl(statusPanel, wx.ID_ANY, style=wx.TE_READONLY)
        # self.currentTime.SetValue('00:00:00')
        self._setCurrentTime()  # Set default zeroed value
        statusSz.Add(self.currentTime, flag=wx.EXPAND|wx.ALL, border=3)

        self.currentStatus = wx.TextCtrl(statusPanel, wx.ID_ANY, style=wx.TE_READONLY)
        # self.currentStatus.SetValue('Stopped')
        self._setCurrentStatus()
        statusSz.Add(self.currentStatus, flag=wx.EXPAND|wx.ALL, border=3)

        self.mainSz.Add(statusSz, flag=wx.ALL|wx.EXPAND, border=10)

    def _initTimerPanel(self):
        """Initialize the timer panel"""
        timerPanel = wx.StaticBox(self.mainPanel, wx.ID_ANY, label='Timer options')
        timerSz = wx.StaticBoxSizer(timerPanel, wx.HORIZONTAL)
        timerOptSz = wx.FlexGridSizer(rows=4, cols=3, vgap=10, hgap=8)

        # Pomodoro duration
        pDurationLabel = wx.StaticText(timerPanel, wx.ID_ANY, label='Pomodoro')
        self.pDurationVal = wx.SpinCtrl(timerPanel, wx.ID_ANY, style=wx.TE_RIGHT, initial=25,
                                         min=1, max=3600)
        self.pDurationUnit = wx.Choice(timerPanel, wx.ID_ANY, choices=self.TIME_UNITS)
        self.pDurationUnit.SetSelection(1)
        timerOptSz.Add(pDurationLabel, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=3)
        timerOptSz.Add(self.pDurationVal, flag=wx.ALL|wx.EXPAND, border=3)
        timerOptSz.Add(self.pDurationUnit, flag=wx.ALL|wx.EXPAND, border=3)

        # Short break duration
        sbDurationLabel = wx.StaticText(timerPanel, wx.ID_ANY, label='Short break')
        self.sbDurationVal = wx.SpinCtrl(timerPanel, wx.ID_ANY, style=wx.TE_RIGHT, initial=5,
                                         min=1, max=3600)
        self.sbDurationUnit = wx.Choice(timerPanel, wx.ID_ANY, choices=self.TIME_UNITS)
        self.sbDurationUnit.SetSelection(1)
        timerOptSz.Add(sbDurationLabel, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=3)
        timerOptSz.Add(self.sbDurationVal, flag=wx.ALL|wx.EXPAND, border=3)
        timerOptSz.Add(self.sbDurationUnit, flag=wx.ALL|wx.EXPAND, border=3)

        # Long break duration
        lbDurationLabel = wx.StaticText(timerPanel, wx.ID_ANY, label='Long break')
        self.lbDurationVal = wx.SpinCtrl(timerPanel, wx.ID_ANY, style=wx.TE_RIGHT, initial=30,
                                         min=1, max=3600)
        self.lbDurationUnit = wx.Choice(timerPanel, wx.ID_ANY, choices=self.TIME_UNITS)
        self.lbDurationUnit.SetSelection(1)
        timerOptSz.Add(lbDurationLabel, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=3)
        timerOptSz.Add(self.lbDurationVal, flag=wx.ALL|wx.EXPAND, border=3)
        timerOptSz.Add(self.lbDurationUnit, flag=wx.ALL|wx.EXPAND, border=3)

        # Pomodoros to long break
        cntLabel = wx.StaticText(timerPanel, wx.ID_ANY, label='Pomodoros to break')
        self.cntVal = wx.SpinCtrl(timerPanel, wx.ID_ANY, initial=4, min=1, max=1000,
                                  style=wx.SP_ARROW_KEYS|wx.ALIGN_LEFT)
        timerOptSz.Add(cntLabel, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        timerOptSz.Add(self.cntVal, flag=wx.ALL|wx.EXPAND)

        timerOptSz.AddGrowableCol(0)
        timerSz.Add(timerOptSz, flag=wx.EXPAND|wx.ALL, border=10)
        self.mainSz.Add(timerSz, flag=wx.EXPAND|wx.ALL, border=10)

    def _initControlButtons(self):
        """Initialize the control buttons in a bottom of MainFrame"""
        btnSz = wx.GridBagSizer(vgap=4, hgap=4)

        self.startBut = wx.Button(self.mainPanel, wx.ID_ANY, label='Start')
        self.Bind(wx.EVT_BUTTON, self.OnStart, self.startBut)
        btnSz.Add(self.startBut, pos=(0,1), flag=wx.ALL|wx.EXPAND, border=3)

        self.pauseBut = wx.Button(self.mainPanel, wx.ID_ANY, label='Pause')
        self.Bind(wx.EVT_BUTTON, self.OnPause, self.pauseBut)
        btnSz.Add(self.pauseBut, pos=(0,2), flag=wx.ALL|wx.EXPAND, border=3)

        self.stopBut = wx.Button(self.mainPanel, wx.ID_ANY, label='Stop')
        self.Bind(wx.EVT_BUTTON, self.OnStop, self.stopBut)
        btnSz.Add(self.stopBut, pos=(0,3), flag=wx.ALL|wx.EXPAND, border=3)

        self.startBut.SetFocus()
        btnSz.AddGrowableRow(0)
        btnSz.AddGrowableCol(0)
        self.mainSz.Add(btnSz, flag=wx.ALIGN_RIGHT|wx.EXPAND, border=10)

    def _initTrayIcon(self):
        """Initialize the tray notification icon"""
        self.icon = TimerTaskBarIcon(self)

    def Refresh(self):
        """Update panel contents"""
        if self.STATUS == 'Running':
            self.startBut.Disable()
            self.pauseBut.Enable()
            self.stopBut.Enable()
        elif self.STATUS == 'Paused':
            self.startBut.Enable()
            self.pauseBut.Disable()
            self.stopBut.Enable()
        else:  # Stopped
            self.startBut.Enable()
            self.pauseBut.Disable()
            self.stopBut.Disable()


        self._setCurrentTime()
        self._setCurrentStatus()
        self._setTitle()

    def format_timedelta(self, td):
        """Format timevalue in seconds to HH:MM:SS format

        :type td: datetime.timedelta
        """
        h = td.seconds // 3600
        m, s = divmod(td.seconds, 60)
        return '{:02d}:{:02d}:{:02d}'.format(h, m, s)

    def _setCurrentStatus(self):
        """Set current status in UI"""
        self.currentStatus.SetValue(self.STATUS)

    def _setCurrentTime(self):
        """Sets actual timer value to currentTime element"""
        remain = self.format_timedelta(self.t_remain)
        self.currentTime.SetValue(remain)

    def _setTitle(self):
        """Change frame's title according timer current status"""
        if self.STATUS in ('Running', 'Paused'):
            remain = self.format_timedelta(self.t_remain)
            title = ' '.join(['wxPomodoro:', self.STATUS.lower(), remain, 'left'])
        else:  # Stopped
            title = 'wxPomodoro: ' + self.STATUS.lower()

        self.SetTitle(title)

    def _getUserInput(self):
        """Get input from UI forms"""
        def get_secs(valElement, unitElement):
            """Return current time in seconds according time unit choice in UI"""
            val = valElement.GetValue()
            if unitElement.GetSelection() == 0:  # seconds
                return int(val)
            if unitElement.GetSelection() == 1:  # minutes
                return int(val)*60
            if unitElement.GetSelection() == 2:  # hours
                return int(val)*3600

        self.p_dur = get_secs(self.pDurationVal, self.pDurationUnit)
        self.sb_dur = get_secs(self.sbDurationVal, self.sbDurationUnit)
        self.lb_dur = get_secs(self.lbDurationVal, self.lbDurationUnit)

    def TimerLoop(self, event):
        self.t_remain = self.t_remain - (datetime.datetime.now() - self.t_tick)
        self.t_tick = datetime.datetime.now()

        if self.t_remain.total_seconds() <= 0:  # Finish current cycle
            self.timer.Stop()
            self.STATUS = 'Stopped'

        wx.CallAfter(self.Refresh)

    def OnStart(self, event):
        self._getUserInput()
        if self.STATUS == 'Stopped' or not self.t_start:
            self.t_start = datetime.datetime.now()
            self.t_tick = self.t_start
            self.t_stop = self.t_start + datetime.timedelta(seconds=self.p_dur)
            self.t_remain = self.t_stop - self.t_start
        else:  # Continue after pause
            pass
        self.timer.Start(1000)
        self.STATUS = 'Running'
        wx.CallAfter(self.Refresh)

    def OnPause(self, event):
        self.timer.Stop()
        self.STATUS = 'Paused'
        wx.CallAfter(self.Refresh)

    def OnStop(self, event):
        self.timer.Stop()
        self.t_remain = self.t_start = self.t_stop = self.t_tick = datetime.timedelta()
        self.STATUS = 'Stopped'
        wx.CallAfter(self.Refresh)

