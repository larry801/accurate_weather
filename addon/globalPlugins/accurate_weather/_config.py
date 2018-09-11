# coding=utf-8
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import languageHandler
from configobj import ConfigObj
import ui
import globalVars
import os
import json
import addonHandler
from io import open
from .caiyun import WeatherDataProvider as ColorfulClouds
addonHandler.initTranslation()
config = None
ini_file_name = "AccurateWeather.ini"
json_file_name = "AccurateWeather.json"

config_spec = """
[General]
copy_to_clipboard = boolean(default=False)
provider=string
report_location = list
[Location]
location_count=integer
[[__many__]]
name=string(max=25)
lat=floats(min=-180, max=180)
lng=floats(min=-90, max=90)
woeID=string(max=25)
[provider]
[[Colorful Cloud]]

[[Yahoo]]
[unit]
temperature=option(C,F,K)
pressure=option(mmHg,Pa)
"""


def load_ini():
    global config
    config_path = os.path.join(globalVars.appArgs.configPath, ini_file_name)
    if os.path.isfile(config_path):
        try:
            config = ConfigObj(infile=config_path,
                               create_empty=True,
                               configspec=config_spec,
                               file_error=True
                               )
        except IOError:
            ui.message(_("Cannot read config file"))
    else:
        config.restore_defaults()
        config.write()


def load_json():
    global config
    path = os.path.join(globalVars.appArgs.configPath, json_file_name)
    if os.path.exists(path) and os.path.isfile(path):
        try:
            config = json.load(open(path))
        except:
            load_default()
    else:
        load_default()


def load_default():
    global config
    default_path = os.path.join(globalVars.appArgs.configPath,
                                "addons",
                                "accurate_weather",
                                "default.json")
    config = json.load(open(default_path))
    save_json()


def save_json():
    path = os.path.join(globalVars.appArgs.configPath, json_file_name)
    json.dump(config, open(path, 'wb'))


def save_location(location, slot_number):
    """
    Save location to config
    :param slot_number: int
    :param location: Location
    :return:
    """
    global config
    config["locations"][slot_number] = location
    save_json()


def add_location(location):
    count = len(config["locations"])
    config["locations"].append(location)
    config["location_report_sequence"].append(count)
    save_json()


def delete_location(num):
    global config
    config["locations"].pop(num)
    for i in range(config["location_report_sequence"]):
        value = config["location_report_sequence"][i]
        is_disabled = False
        if value < 0:
            original_index = abs(value) - 1
            is_disabled = True
        else:
            original_index = i
        if original_index < num:
            continue
        else:
            if original_index == num:
                config["location_report_sequence"].remove(i)
            else:
                if is_disabled:
                    config["location_report_sequence"][i] = value + 1
                else:
                    config["location_report_sequence"][i] = value - 1
    save_json()


def get_location(slot_number):
    """
    Get location on a specific slot
    :param slot_number:
    :return: Location
    """
    return config["locations"][slot_number]


def copy_to_clipboard():
    return config["copy_to_clipboard"]


def set_copy_to_clipboard(value):
    config["copy_to_clipboard"] = value


def provider_id():
    return config["provider_id"]


def set_provider_id(value):
    config["provider_id"] = value


def real_time_report_sequence():
    return config["providers"][str(provider_id())]["realtime_seq"]


def forecast_report_sequence():
    return config["providers"][provider_id()]["forecast_seq"]


providers_list = [ColorfulClouds]


def cc_api_token():
    try:
        val =  config["providers"]["0"]["token"]
    except KeyError:
        # this is the test token on http://wiki.caiyunapp.com/index.php/彩云天气API/v2
        config["providers"]["0"]["token"] = "TAkhjf8d1nlSlspN"
        save_json()
        val = config["providers"]["0"]["token"]
    return val


def cc_proxy_base_url():
    try:
        value = config["providers"]["0"]["reverse_proxy_url"]
    except KeyError:
        config["providers"]["0"]["reverse_proxy_url"] = r"http://caiyun?token="
        save_json()
        value = config["providers"]["0"]["reverse_proxy_url"]
    return value


def cc_access_method():
    try:
        val = config["providers"]["0"]["access_method"]
    except KeyError:
        val = 0
        config["providers"]["0"]["access_method"] = 0
        save_json()
    return val


def cc_config_or_default(key_name, default_value):
    try:
        val = config["providers"]["0"][key_name]
    except KeyError:
        val = default_value
        config["providers"]["0"][key_name] = default_value
        save_json()
    return val

def set_cc_config(key_name, value):
    config["providers"]["0"][key_name] = value
    save_json()


def set_cc_access_method(value):
    set_cc_config("access_method", value)


def set_cc_description_language(value):
    set_cc_config("description_language", value)


def get_cc_description_language():
    lang = languageHandler.getLanguage()
    if lang == 'zh_CN':
        default_lang = 1
    elif lang == "zh_TW":
        default_lang = 2
    elif lang.startswith("en"):
        default_lang = 0
    else:
        default_lang = 0
    return cc_config_or_default("description_language", default_lang)


def set_cc_api_token(value):
    config["providers"]["0"]["token"] = value
    save_json()
