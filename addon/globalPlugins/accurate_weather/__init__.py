# Accurate Weather: An Add-on for nvda that does <Insert thing here>

# Copyright (C) 2018 LarryWang

# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""accurate_weather:
A global plugin 
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from io import StringIO
from . import reporter
from . import settingsGUI
from . import location
from . import _config
from logHandler import log
import addonHandler
import wx
import gui
import os
import globalPluginHandler
import globalVars
import config
import ui
# We need to initialize translation and localization support:
addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    def script_about(self, evt):
        """
        Show about dialog
        """
        from wx.adv import AboutDialogInfo
        info = AboutDialogInfo()
        info.AddDeveloper("Larry Wang")
        info.SetName("Accurate Weather")
        icon_path = os.path.join(globalVars.appArgs.configPath,
                                 "addons",
                                 "accurate_weather",
                                 "colorfulClouds.png")
        info.SetIcon(wx.Icon(icon_path, wx.BITMAP_TYPE_PNG))
        description = _("The minutely precipitation forecast is jointly produced by China Meteorological Administration and Colorful Clouds Technology")
        info.SetDescription(description)
        wx.adv.AboutBox(info, gui.mainFrame)

    __gestures = {
        "kb:NVDA+alt+shift+w": "about",
        "kb:NVDA+w": "announce_real_time",
        "kb:NVDA+alt+w": "announce_forecast",
        "kb:NVDA+control+alt+shift+w": "open_location_manager"
    }

    def script_open_location_manager(self, evt):
        dlg = settingsGUI.LocationSettings(gui.mainFrame, multiInstanceAllowed=True)
        dlg.ShowModal()

    def script_announce_forecast(self, gesture):
        if not _config.config["locations"]:
            ui.message(_("No locations please set one"))
            return
        provider_class = _config.providers_list[_config.config["provider_id"]]
        provider = provider_class()
        forecast_reporter = reporter.ForecastReporter()
        buffer = StringIO()
        for l in _config.config["location_report_sequence"]:
            if l < 0:
                continue
            this_location = _config.get_location(l)
            provider.forecast_update(this_location)
            buffer.write(forecast_reporter.report(this_location))
        ui.message(buffer.getvalue())

    def script_announce_real_time(self, gesture):
        if not _config.config["locations"]:
            ui.message(_("No locations please set one"))
            return
        provider_class = _config.providers_list[_config.config["provider_id"]]
        provider = provider_class()
        realtime_reporter = reporter.RealTimeReporter()
        buffer = StringIO()
        for l in _config.config["location_report_sequence"]:
            if l < 0:
                continue
            this_location = _config.get_location(l)
            provider.update(this_location)
            report_string = realtime_reporter.report(this_location)
            buffer.write(report_string)
        ui.message(buffer.getvalue())

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        if globalVars.appArgs.secure:
            return
        if config.isAppX:
            return
        _config.load_json()
        location.load_region_code()
        log.info("Accurate weather plugin initialized")
        gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(settingsGUI.AccurateWeatherPanel)
        # self.menu = gui.mainFrame.sysTrayIcon.menu.GetMenuItems()[0].GetSubMenu()
        # self.WeatherMenu = wx.Menu()
        # self.mainItem = self.menu.AppendSubMenu(self.WeatherMenu, _("&Accurate Weather Settings"), _("Show configuration items."))
        # self.locationManagerItem = self.WeatherMenu.Append(wx.ID_ANY, _("Set and &manage your locations..."), _("Displays or allows to set the current locations from a list"))
        # gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_open_location_manager, self.locationManagerItem)
        # self.AboutItem = self.WeatherMenu.Append(wx.ID_ANY, _("&About"), _("Opens the about box"))
        # gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_about, self.AboutItem)
