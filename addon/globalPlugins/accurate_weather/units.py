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
