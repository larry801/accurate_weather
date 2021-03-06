# coding=utf-8
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from gui.settingsDialogs import SettingsPanel, SettingsDialog
import gui
import os
import globalVars
import wx
from gui import guiHelper
from logHandler import log
import ui
from wx import Button
import addonHandler
from . import ObjectListView
from . import _config
from . import location
from . import units
from . import util
import json

addonHandler.initTranslation()
_addonDir = os.path.join(os.path.dirname(__file__), "..", "..").decode("mbcs")
_curAddon = addonHandler.Addon(_addonDir)
_addonSummary = _curAddon.manifest['summary']
confirm_message = _("Yes or no?")


def add_location(lat, lng, name):
    new_location = {
        "latitude": lat,
        "longitude": lng,
        "name": name
    }
    _config.add_location(new_location)


def YesOrNo(parent, question, caption=confirm_message):
    dlg = wx.MessageDialog(parent, question, caption, wx.YES_NO | wx.ICON_QUESTION)
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    return result


class CustomSettingsDialog(wx.Dialog):
    """A settings dialog.
    """
    title = ""

    def __init__(self, parent,
                 resizeable=False,
                 hasApplyButton=False,
                 settingsSizerOrientation=wx.VERTICAL,
                 multiInstanceAllowed=False):
        windowStyle = wx.DEFAULT_DIALOG_STYLE | (wx.RESIZE_BORDER if resizeable else 0)
        super(CustomSettingsDialog, self).__init__(parent, title=self.title, style=windowStyle)
        self.hasApply = hasApplyButton

        # the wx.Window must be constructed before we can get the handle.
        import windowUtils
        self.scaleFactor = windowUtils.getWindowScalingFactor(self.GetHandle())

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.settingsSizer = wx.BoxSizer(settingsSizerOrientation)
        self.makeSettings(self.settingsSizer)

        self.mainSizer.Add(self.settingsSizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL | wx.EXPAND,
                           proportion=1)
        self.mainSizer.Add(wx.StaticLine(self), flag=wx.EXPAND)

        buttonSizer = guiHelper.ButtonHelper(wx.HORIZONTAL)
        # Translators: The Ok button on a NVDA dialog. This button will accept any changes and dismiss the dialog.
        buttonSizer.addButton(self, label=_("OK"), id=wx.ID_OK)
        # Translators: The cancel button on a NVDA dialog. This button will discard any changes and dismiss the dialog.
        buttonSizer.addButton(self, label=_("Cancel"), id=wx.ID_CANCEL)
        if hasApplyButton:
            # Translators: The Apply button on a NVDA dialog. This button will accept any changes but will not dismiss the dialog.
            buttonSizer.addButton(self, label=_("Apply"), id=wx.ID_APPLY)

        self.mainSizer.Add(
            buttonSizer.sizer,
            border=guiHelper.BORDER_FOR_DIALOGS,
            flag=wx.ALL | wx.ALIGN_RIGHT
        )

        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)

        self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.onCancel, id=wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.onApply, id=wx.ID_APPLY)
        self.Bind(wx.EVT_CHAR_HOOK, self._enterActivatesOk_ctrlSActivatesApply)

        self.postInit()
        self.CentreOnScreen()

    def _enterActivatesOk_ctrlSActivatesApply(self, evt):
        """Listens for keyboard input and triggers ok button on enter and triggers apply button when control + S is
        pressed. Cancel behavior is built into wx.
        Pressing enter will also close the dialog when a list has focus
        (e.g. the list of symbols in the symbol pronunciation dialog).
        Without this custom handler, enter would propagate to the list control (wx ticket #3725).
        """
        if evt.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.ProcessEvent(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_OK))
        elif self.hasApply and evt.UnicodeKey == ord(u'S') and evt.controlDown:
            self.ProcessEvent(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_APPLY))
        else:
            evt.Skip()

    def makeSettings(self, sizer):
        """Populate the dialog with settings controls.
        Subclasses must override this method.
        @param sizer: The sizer to which to add the settings controls.
        @type sizer: wx.Sizer
        """
        raise NotImplementedError

    def postInit(self):
        """Called after the dialog has been created.
        For example, this might be used to set focus to the desired control.
        Sub-classes may override this method.
        """

    def onOk(self, evt):
        """Take action in response to the OK button being pressed.
        Sub-classes may extend this method.
        This base method should always be called to clean up the dialog.
        """
        self.DestroyChildren()
        self.Destroy()
        self.SetReturnCode(wx.ID_OK)

    def onCancel(self, evt):
        """Take action in response to the Cancel button being pressed.
        Sub-classes may extend this method.
        This base method should always be called to clean up the dialog.
        """
        self.DestroyChildren()
        self.Destroy()
        self.SetReturnCode(wx.ID_CANCEL)

    def onApply(self, evt):
        """Take action in response to the Apply button being pressed.
        Sub-classes may extend or override this method.
        This base method should be called to run the postInit method.
        """
        self.postInit()
        self.SetReturnCode(wx.ID_APPLY)

    def scaleSize(self, size):
        """Helper method to scale a size using the logical DPI
        @param size: The size (x,y) as a tuple or a single numerical type to scale
        @returns: The scaled size, returned as the same type"""
        if isinstance(size, tuple):
            return self.scaleFactor * size[0], self.scaleFactor * size[1]
        return self.scaleFactor * size


class ManuallyInputLocationDialog(CustomSettingsDialog):
    name_input = None  # type: wx.TextCtrl
    latitude_input = None  # type: wx.TextCtrl
    longitude_input = None  # type: wx.TextCtrl

    def onOk(self, evt):
        name = self.name_input.GetValue()
        lat = self.latitude_input.GetValue()
        lng = self.longitude_input.GetValue()
        if not util.isValidLatitude(lat):
            ui.message(_("Please input a valid latitude value"))
            self.latitude_input.SetFocus()
            return
        if not util.isValidLongitude(lng):
            self.longitude_input.SetFocus()
            ui.message(_("Please input a valid longitude value"))
            return
        add_location(lat, lng, name)
        super(ManuallyInputLocationDialog, self).onOk(evt)

    def makeSettings(self, sizer):
        helper = guiHelper.BoxSizerHelper(self, sizer=sizer)
        self.name_input = helper.addLabeledControl(_("Name of new location"), wx.TextCtrl)
        self.latitude_input = helper.addLabeledControl(_("Latitude of new location"), wx.TextCtrl)
        self.longitude_input = helper.addLabeledControl(_("Longitude of new location"), wx.TextCtrl)


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


class LocationSettings(CustomSettingsDialog):
    location_list = None  # type: ObjectListView.ObjectListView

    title = _("Location manager")

    def onOk(self, evt):
        self.EndModal(wx.ID_OK)

    def onCancel(self, evt):
        self.EndModal(wx.ID_CANCEL)

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
            # Translators: The label for a button in location manager to add new entries.
            label=_("&Add")
        ).Bind(wx.EVT_BUTTON, self.OnAddClick)

        bHelper.addButton(
            parent=self,
            # Translators: The label for a button in location manager to edit existing entries.
            label=_("&Edit")
        ).Bind(wx.EVT_BUTTON, self.OnEditClick)

        bHelper.addButton(
            parent=self,
            # Translators: The label for a button in location manager to remove existing entries.
            label=_("&Remove")
        ).Bind(wx.EVT_BUTTON, self.OnRemoveClick)
        sHelper.addItem(bHelper)

    def refresh_list(self):
        self.location_list.SetObjects(_config.config["locations"])

    def postInit(self):
        self.location_list.SetFocus()

    def OnAddClick(self, evt):
        entryDialog = ChooseMethodsToAddLocation(self, multiInstanceAllowed=True)
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


class ChooseMethodsToAddLocation(CustomSettingsDialog):
    geo_button = None  # type: Button
    China_administrative_division_button = None  # type: Button
    manually_input_button = None  # type: Button
    detect_by_ip_address_button = None  # type: Button
    title = _("How to add new location?")

    def onDetectByIp(self, evt):
        data = util.get_data_from_url(r"https://ifconfig.co/json")
        content = json.loads(data)
        lng = content["longitude"]
        lat = content["latitude"]
        city_name = content["city"]
        country = content["country"]
        message = _("According to your ip address You are in{city_name},{country}. Do you want to add this one?")
        msg = message.format(city_name=city_name,
                             country=country)
        if YesOrNo(self, msg):
            new_location = {
                "latitude": lat,
                "longitude": lng,
                "name": city_name
            }
            _config.add_location(new_location)

    def onGeoNames(self, evt):
        pass

    def onChinaAdministrativeDivisions(self, evt):
        entryDialog = ChooseFromChinaAdministrativeDivisionDialog(self, multiInstanceAllowed=True)
        entryDialog.ShowModal()

    def onManuallyInput(self, evt):
        entryDialog = ManuallyInputLocationDialog(self, multiInstanceAllowed=True)
        entryDialog.ShowModal()

    def makeSettings(self, sizer):
        settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)

        self.geo_button = wx.Button(self,
                                    label=_("Search in geonames"))
        self.geo_button.Bind(wx.EVT_BUTTON,
                             self.onGeoNames)
        settingsSizerHelper.addItem(self.geo_button)

        self.detect_by_ip_address_button = wx.Button(self,
                                                     label=_("Detect your location by ip address"))
        self.detect_by_ip_address_button.Bind(wx.EVT_BUTTON,

                                              self.onDetectByIp)
        settingsSizerHelper.addItem(self.detect_by_ip_address_button)

        self.manually_input_button = wx.Button(self,
                                               label=_("Manually input latitude and longitude"))
        self.manually_input_button.Bind(wx.EVT_BUTTON,
                                        self.onManuallyInput)
        settingsSizerHelper.addItem(self.manually_input_button)

        self.China_administrative_division_button = wx.Button(self,
                                                              label=_("Choose from administrative divisions in China"))
        self.China_administrative_division_button.Bind(wx.EVT_BUTTON,
                                                       self.onChinaAdministrativeDivisions)
        settingsSizerHelper.addItem(self.China_administrative_division_button)


# noinspection PyTypeChecker
class ChooseFromChinaAdministrativeDivisionDialog(CustomSettingsDialog):
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
        add_location(lat, lng, name)
        super(ChooseFromChinaAdministrativeDivisionDialog, self).onOk(evt)


class AccurateWeatherPanel(SettingsPanel):
    unit_settings_button = None  # type: Button
    copyToClipBoardCheckBox = None  # type: wx.CheckBox
    choose_provider_list = None  # type: wx.Choice
    location_manager_button = None  # type: wx.Button
    edit_location_sequence_button = None  # type: wx.Button
    provider_specific_settings_button = None  # type: wx.Button
    show_about_box_button = None  # type: wx.Button

    def onSave(self):
        _config.set_provider_id(self.choose_provider_list.GetSelection())
        _config.setCopyToClipBoard(self.copyToClipBoardCheckBox.IsChecked())

    def onLocationManager(self, evt):
        dlg = LocationSettings(self)
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

    def onAbout(self, evt):
        """
        Show about dialog
        """
        from wx.adv import AboutDialogInfo
        info = AboutDialogInfo()
        info.AddDeveloper("Larry Wang")
        info.SetName(_addonSummary)
        icon_path = os.path.join(globalVars.appArgs.configPath,
                                 "addons",
                                 "accurate_weather",
                                 "colorfulClouds.png")
        info.SetIcon(wx.Icon(icon_path, wx.BITMAP_TYPE_PNG))
        description = _(
            "The precipitation forecast on per minute basis is jointly produced by China Meteorological Administration and Colorful Clouds Technology")
        info.SetDescription(description)
        wx.adv.AboutBox(info, self)

    title = _("Accurate Weather")

    def makeSettings(self, sizer):
        sHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)
        label_of_provider_list = _("Provider:")
        choice_of_provider_list = [x.name for x in _config.providers_list]
        self.choose_provider_list = sHelper.addLabeledControl(label_of_provider_list, wx.Choice,
                                                              choices=choice_of_provider_list)
        pid = _config.provider_id()
        self.choose_provider_list.SetSelection(pid)

        copyToClipboardLabel = _("Copy announced weather condition to clipboard")
        self.copyToClipBoardCheckBox = wx.CheckBox(self, label=copyToClipboardLabel)
        sHelper.addItem(self.copyToClipBoardCheckBox)

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

        self.show_about_box_button = wx.Button(self, label=_("Open about dialog"))
        self.show_about_box_button.Bind(wx.EVT_BUTTON, self.onAbout)
        sHelper.addItem(self.show_about_box_button)


class UnitSettings(CustomSettingsDialog):
    unit_lists = {}
    title = _("Unit Settings")

    def makeSettings(self, sizer):
        sHelper = guiHelper.BoxSizerHelper(self, sizer=sizer)
        for e in units.unit_entries.keys():
            self.unit_lists[e] = sHelper.addLabeledControl(units.unit_entries[e]["label"],
                                                           wx.Choice,
                                                           choices=units.unit_entries[e]["choices"])
            self.unit_lists[e].SetSelection(_config.unit_config_or_default(e, 0))

    def onOk(self, evt):
        for e in units.unit_entries.keys():
            _config.set_unit_config(self.unit_lists[e].GetSelection())
        super(UnitSettings, self).onOk(evt)


class ColorfulClouds(CustomSettingsDialog):
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
        super(ColorfulClouds, self).onOk(evt)


