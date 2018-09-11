# coding=utf-8
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from gui.settingsDialogs import SettingsPanel, SettingsDialog
import gui
import wx
from gui import guiHelper
from logHandler import log
from wx import Button
import addonHandler
from . import ObjectListView
from . import _config
from . import location
from . import units

addonHandler.initTranslation()


class EditLocationNameDlg(wx.Dialog):

    def __init__(self, parent, index):
        wx.Dialog.__init__(self, parent, title=_(u"Location Name Editor"),
                           size=(550, 330))
        pan = wx.Panel(self)
        self.index = index
        self.contents = wx.TextCtrl(pan)
        self.contents.SetValue(_config.get_location(index)["name"])
        saveButton = wx.Button(pan, label=_(u"Save and exit (&S)"))
        saveButton.Bind(wx.EVT_BUTTON, self.onSave)
        exitButton = wx.Button(pan, label=_(u"Exit (&E)"))
        exitButton.Bind(wx.EVT_BUTTON, self.onExit)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.contents, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        hbox = wx.BoxSizer()
        hbox.Add(exitButton, proportion=0, flag=wx.LEFT, border=5)
        hbox.Add(saveButton, proportion=0, flag=wx.LEFT, border=5)
        vbox.Add(hbox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        pan.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.contents.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        pan.SetSizer(vbox)

    def onKeyDown(self, evt):
        key = evt.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.EndModal(0)
            return
        evt.Skip()

    def onExit(self, evt):
        self.EndModal(0)

    def onSave(self, evt):
        _config.config["locations"][self.index]["name"] = self.contents.GetValue()
        _config.save_json()
        self.EndModal(0)


class LocationSettings(SettingsDialog):
    location_list = None  # type: ObjectListView.ObjectListView

    title = _("Location manager")

    def makeSettings(self, sizer):
        sHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)
        entriesLabelText = _("&Location entries")

        self.location_list = sHelper.addLabeledControl(entriesLabelText, ObjectListView.ObjectListView,
                                                       style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=(550, 350))
        self.location_list.SetColumns([
            ObjectListView.ColumnDefn("Name", "left", 220, "name"),
            ObjectListView.ColumnDefn("Latitude", "left", 220, "latitude"),
            ObjectListView.ColumnDefn("Longitude", "left", 220, "longitude")
        ])
        self.refresh_list()
        bHelper = guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
        bHelper.addButton(
            parent=self,
            # Translators: The label for a button in speech dictionaries dialog to add new entries.
            label=_("&Add")
        ).Bind(wx.EVT_BUTTON, self.OnAddClick)

        bHelper.addButton(
            parent=self,
            # Translators: The label for a button in speech dictionaries dialog to edit existing entries.
            label=_("&Edit")
        ).Bind(wx.EVT_BUTTON, self.OnEditClick)

        bHelper.addButton(
            parent=self,
            # Translators: The label for a button in speech dictionaries dialog to remove existing entries.
            label=_("&Remove")
        ).Bind(wx.EVT_BUTTON, self.OnRemoveClick)
        sHelper.addItem(bHelper)

    def refresh_list(self):
        self.location_list.SetObjects(_config.config["locations"])

    def postInit(self):
        self.location_list.SetFocus()

    def OnAddClick(self, evt):
        entryDialog = AddLocationEntryDialog(self, multiInstanceAllowed=True)
        entryDialog.ShowModal()
        self.refresh_list()

    def OnEditClick(self, evt):
        if self.location_list.GetSelectedItemCount() != 1:
            return
        editIndex = self.location_list.GetFirstSelected()
        if editIndex < 0:
            return
        else:
            dlg = EditLocationNameDlg(self, editIndex)
            dlg.ShowModal()
        self.refresh_list()

    def OnRemoveClick(self, evt):
        if self.location_list.GetSelectedItemCount() != 1:
            return
        editIndex = self.location_list.GetFirstSelected()
        if editIndex < 0:
            return
        else:
            _config.delete_location(editIndex)
        self.refresh_list()


class ChooseMethodsToAddLocation(SettingsDialog):
    geo_button = None  # type: Button
    China_administrative_division_button = None  # type: Button
    manually_input_button = None  # type: Button
    title = _("How to add new location?")

    def onGeoNames(self, evt):
        pass

    def onChinaAdministrativeDivisions(self, evt):
        pass

    def onManuallyInput(self, evt):
        pass

    def makeSettings(self, sizer):
        settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)

        self.geo_button = wx.Button(self,
                                    label=_("Search in geonames"))
        self.geo_button.Bind(wx.EVT_BUTTON,
                             self.onGeoNames)
        settingsSizerHelper.addItem(self.geo_button)

        self.manually_input_button = wx.Button(self,
                                               label=_("Search in geonames"))
        self.manually_input_button.Bind(wx.EVT_BUTTON,
                                        self.onManuallyInput)
        settingsSizerHelper.addItem(self.manually_input_button)

        self.China_administrative_division_button = wx.Button(self,
                                                              label=_("Choose from administrative divisions in China"))
        self.China_administrative_division_button.Bind(wx.EVT_BUTTON,
                                                       self.onChinaAdministrativeDivisions)
        settingsSizerHelper.addItem(self.China_administrative_division_button)


class AddLocationEntryDialog(SettingsDialog):
    province_list = None  # type: wx.Choice
    region_list = None  # type: wx.Choice
    country_list = None  # type: wx.Choice
    title = _("Add a location")

    def makeSettings(self, sizer):
        settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)

        provinceChoice = [x['name'] for x in location.province_list]
        province_label_text = "省"

        self.province_list = settingsSizerHelper.addLabeledControl(province_label_text, wx.Choice,
                                                                   choices=provinceChoice)
        self.Bind(wx.EVT_CHOICE, self.OnProvinceChange, self.province_list)

        region_label = "市"
        country_label = "县"

        self.region_list = settingsSizerHelper.addLabeledControl(region_label, wx.Choice)
        self.Bind(wx.EVT_CHOICE, self.OnRegionChange, self.region_list)

        self.country_list = settingsSizerHelper.addLabeledControl(country_label, wx.Choice)

    def OnProvinceChange(self, evt):
        location.level2_list = location.province_list[self.province_list.GetSelection()]['children']
        if len(location.level2_list) > 0:
            region_names = [x['name'] for x in location.level2_list]
            self.region_list.SetItems(region_names)
        self.country_list.SetItems([])

    def OnRegionChange(self, evt):
        location.level3_list = location.level2_list[self.region_list.GetSelection()]['children']
        country_names = [x['name'] for x in location.level3_list]
        self.country_list.SetItems(country_names)

    def onOk(self, evt):
        region_index = self.country_list.GetSelection()
        region_code = location.level3_list[region_index]['code']
        lat = location.code_to_geo_dict[region_code]["lat"]
        name = location.code_to_geo_dict[region_code]["name"]
        lng = location.code_to_geo_dict[region_code]["lng"]
        new_location = {
            "latitude": lat,
            "longitude": lng,
            "name": name
        }
        _config.add_location(new_location)
        self.DestroyChildren()
        self.Destroy()
        self.SetReturnCode(wx.ID_OK)


class AccurateWeatherPanel(SettingsPanel):
    unit_settings_button = None  # type: Button
    choose_provider_list = None  # type: wx.Choice
    location_manager_button = None  # type: wx.Button
    edit_location_sequence_button = None  # type: wx.Button
    provider_specific_settings_button = None  # type: wx.Button

    def onSave(self):
        _config.provider_id = self.choose_provider_list.GetSelection()

    def onLocationManager(self, evt):
        dlg = LocationSettings(self, multiInstanceAllowed=True)
        dlg.ShowModal()

    def onUnitSettings(self, evt):
        dlg = UnitSettings(self, multiInstanceAllowed=True)
        dlg.ShowModal()

    def onProviderSettings(self, evt):
        pid = _config.provider_id()
        if pid == 0:
            dlg = ColorfulClouds(self, multiInstanceAllowed=True)
        dlg.ShowModal()

    def onEditSequence(self, evt):
        items = [x["name"] for x in _config.config["locations"]]
        order = _config.config["location_report_sequence"]
        if len(order) != len(items):
            order = range(len(items))
        dlg = wx.RearrangeDialog(self,
                                 _("You can also uncheck the items you don't want to hear its report at all."),
                                 _("Sort the locations"),
                                 order, items)
        if dlg.ShowModal() == wx.ID_OK:
            _config.config["location_report_sequence"] = dlg.GetOrder()
            _config.save_json()

    title = _("Accurate Weather")

    def makeSettings(self, sizer):
        sHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)
        label_of_provider_list = _("Provider:")
        choice_of_provider_list = [x.name for x in _config.providers_list]
        self.choose_provider_list = sHelper.addLabeledControl(label_of_provider_list, wx.Choice,
                                                              choices=choice_of_provider_list)
        pid = _config.config["provider_id"]
        self.choose_provider_list.SetSelection(pid)

        self.provider_specific_settings_button = wx.Button(self, label=_("Open provider specific settings"))
        self.provider_specific_settings_button.Bind(wx.EVT_BUTTON, self.onProviderSettings)
        sHelper.addItem(self.provider_specific_settings_button)

        self.location_manager_button = wx.Button(self, label=_("Open location manager"))
        self.location_manager_button.Bind(wx.EVT_BUTTON, self.onLocationManager)
        sHelper.addItem(self.location_manager_button)

        self.edit_location_sequence_button = wx.Button(self, label=_("Change report sequence"))
        self.edit_location_sequence_button.Bind(wx.EVT_BUTTON, self.onEditSequence)
        sHelper.addItem(self.edit_location_sequence_button)

        self.unit_settings_button = wx.Button(self, label=_("Open unit settings"))
        self.unit_settings_button.Bind(wx.EVT_BUTTON, self.onUnitSettings)
        sHelper.addItem(self.unit_settings_button)


class UnitSettings(SettingsDialog):
    unit_lists = {}
    title = _("Unit Settings")

    def makeSettings(self, sizer):
        sHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)
        for e in units.unit_entries.keys():
            self.unit_lists[e] = sHelper.addLabeledControl(units.unit_entries[e]["label"],
                                                           wx.Choice,
                                                           choices=units.unit_entries[e]["choices"])
            self.unit_lists[e].SetSelection(_config.config["units"][e])

    def onOk(self, evt):
        for e in units.unit_entries.keys():
            _config.config["units"][e] = self.unit_lists[e].GetSelection()
            _config.save_json()
        self.DestroyChildren()
        self.Destroy()
        self.SetReturnCode(wx.ID_OK)


class ColorfulClouds(SettingsDialog):
    title = _("Colorful Clouds settings")

    api_token_input = None  # type: wx.TextCtrl
    access_method_list = None  # type: wx.Choice
    description_language_list = None  # type: wx.Choice

    def makeSettings(self, sizer):
        sHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)

        access_method_label = _("How to get data from API")
        access_method_choices = [_("Through proxy"),
                                 _("Use your own API token")]
        self.access_method_list = sHelper.addLabeledControl(access_method_label,
                                                            wx.Choice,
                                                            choices=access_method_choices)
        self.access_method_list.SetSelection(_config.cc_access_method())
        language_choices = [
            _("English"),
            _("Simplified Chinese"),
            _("Traditional Chinese (Taiwan)")
        ]

        self.description_language_list = sHelper.addLabeledControl(_("Language used in forecast description"),
                                                                   wx.Choice,
                                                                   choices=language_choices)
        self.description_language_list.SetSelection(_config.get_cc_description_language())

        self.api_token_input = sHelper.addLabeledControl(_("API Key"),
                                                         wx.TextCtrl)
        self.api_token_input.SetValue(_config.cc_api_token())
        sHelper.addItem(self.api_token_input)

    def onOk(self, evt):
        _config.set_cc_api_token(self.api_token_input.GetValue())
        _config.set_cc_access_method(self.access_method_list.GetSelection())
        _config.set_cc_description_language(self.description_language_list.GetSelection())
        self.DestroyChildren()
        self.Destroy()
        self.SetReturnCode(wx.ID_OK)
