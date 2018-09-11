from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import addonHandler

addonHandler.initTranslation()

unit_entries = {
    "temperature": {
        "label": _("Temperature"),
        "choices": [_("Celsius"), _("Fahrenheit"), _("Kelvin")]
    },
    "wind_speed": {
        "label": _("Wind speed"),
        "choices": [_("kilometer per hour"), _("Meter per second"), _("Levels")]
    }
}

TEMPERATURE_CELSIUS_UNIT_ID = 0
TEMPERATURE_FAHRENHEIT_UNIT_ID = 1
TEMPERATURE_KELVIN_UNIT_ID = 2


def temperature_convert_from(value, unit_id):
    try:
        numeric_value = float(value)
    except ValueError:
        return None
    if unit_id == 1:
        out = (numeric_value - 32) * 5 / 9
        return str(out)
    else:
        out = numeric_value - 273.15
        return str(out)


def temperature_convert_to(value, unit_id):
    try:
        numeric_value = float(value)
    except ValueError:
        return None
    if unit_id == 1:
        out = (numeric_value * 9 / 5) + 32
        return out
    elif unit_id == 2:
        out = numeric_value + 273.15
        return out
    else:
        return value


WIND_SPEED_KPH_UID = 0
WIND_SPEED_MPS_UID = 1
WIND_SPEED_LEVEL_UID = 2


def wind_speed_to(value, wid):
    try:
        numeric_value = float(value)
    except ValueError:
        return None
    if wid == WIND_SPEED_KPH_UID:
        return value
    elif wid == WIND_SPEED_MPS_UID:
        converted_value = numeric_value / 3.6
        return converted_value
    elif wid == WIND_SPEED_LEVEL_UID:
        if numeric_value < 1:
            wind_level_number = 0
        elif numeric_value < 5:
            wind_level_number = 1
        elif numeric_value < 11:
            wind_level_number = 2
        elif numeric_value < 19:
            wind_level_number = 3
        elif numeric_value < 28:
            wind_level_number = 4
        elif numeric_value < 38:
            wind_level_number = 5
        elif numeric_value < 49:
            wind_level_number = 6
        elif numeric_value < 61:
            wind_level_number = 7
        elif numeric_value < 74:
            wind_level_number = 8
        elif numeric_value < 88:
            wind_level_number = 9
        elif numeric_value < 102:
            wind_level_number = 10
        elif numeric_value < 117:
            wind_level_number = 11
        elif numeric_value < 133:
            wind_level_number = 12
        elif numeric_value < 149:
            wind_level_number = 13
        elif numeric_value < 166:
            wind_level_number = 14
        elif numeric_value < 183:
            wind_level_number = 15
        elif numeric_value < 201:
            wind_level_number = 16
        else:
            wind_level_number = 17
        return wind_level_number


def wind_speed_from(value, wid):
    try:
        numeric_value = float(value)
    except ValueError:
        return None
    if wid == WIND_SPEED_KPH_UID:
        return value
    elif wid == WIND_SPEED_MPS_UID:
        converted_value = numeric_value * 3.6
        return converted_value




sky_con_dic = {
    'CLOUDY': _('Cloudy'),
    'CLEAR_DAY': _('Sunny'),
    'CLEAR_NIGHT': _('Sunny'),
    'PARTLY_CLOUDY_DAY': _('Partly Cloudy'),
    'PARTLY_CLOUDY': _("Partly Cloudy"),
    'PARTLY_CLOUDY_NIGHT': _('Partly Cloudy'),
    'RAIN': _('Rain'),
    'WIND': _('Wind'),
    'FOG': _('Fog'),
    'SNOW': _('Snow'),
    "HAZE": _("Haze")
}
