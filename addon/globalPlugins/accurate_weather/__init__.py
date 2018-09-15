# Accurate Weather: An Add-on for nvda that does <Insert thing here>

# Copyright (C) 2018 LarryWang

# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

"""accurate_weather:
A global plugin 
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import api
from io import StringIO
from . import reporter
from . import settingsGUI
from . import location
from . import _config
from logHandler import log
import addonHandler
import gui
import os
import globalPluginHandler
import globalVars
import config
import ui
# We need to initialize translation and localization support:
addonHandler.initTranslation()
_addonDir = os.path.join(os.path.dirname(__file__), "..", "..").decode("mbcs")
_curAddon = addonHandler.Addon(_addonDir)
_addonSummary = _curAddon.manifest['summary']


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    scriptCategory = _addonSummary

    # def script_about(self, evt):
    #     pass
    #
    # script_about.__doc__ = _("Open about dialog")

    def script_open_location_manager(self, evt):
        dlg = settingsGUI.LocationSettings(gui.mainFrame)
        gui.runScriptModalDialog(dlg)

    script_open_location_manager.__doc__ = _("Open location manager")

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
        msg = buffer.getvalue()
        self.copyAndAnnounce(msg)

    @staticmethod
    def copyAndAnnounce(message):
        if _config.copyToClipboard():
            api.copyToClip(message)
        ui.message(message)

    script_announce_forecast.__doc__ = _("Announce weather forecast")

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
        msg = buffer.getvalue()
        self.copyAndAnnounce(msg)

    script_announce_real_time.__doc__ = _("Announce realtime weather condition")

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

    __gestures = {
        # "kb:NVDA+alt+shift+w": "about",
        "kb:NVDA+control+alt+shift+w": "open_location_manager",
        "kb:NVDA+w": "announce_real_time",
        "kb:NVDA+alt+w": "announce_forecast",
    }
