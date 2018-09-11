from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from . import _config
from io import StringIO
from . import units
import addonHandler
addonHandler.initTranslation()


class ForecastReporter(object):

    location = None

    @property
    def basic_info(self):
        tid = _config.config["units"]["temperature"]
        t_name = units.unit_entries["temperature"]["choices"][tid]
        sky_con_name = units.sky_con_dic[self.location["forecast"]["raw"]["daily"]["skycon"][0]["value"]]
        t_min_ori = self.location["forecast"]["raw"]["daily"]["temperature"][0]["min"]
        t_min = units.temperature_convert_to(t_min_ori, tid)
        t_max_ori = self.location["forecast"]["raw"]["daily"]["temperature"][0]["max"]
        t_max = units.temperature_convert_to(t_max_ori, tid)
        report = _("In {name} the weather report for today is {condition} with the maximum temperature of {max}degrees {unit} with the minimum temperature of {min} degrees {unit}.")
        report = report.format(
            name=self.location["name"],
            max=t_max,
            min=t_min,
            unit=t_name,
            condition=sky_con_name
        )
        return report

    def report(self, location):
        self.location = location
        seq = _config.real_time_report_sequence()
        report_buffer = StringIO()
        for e in seq:
            report_buffer.write(self.__getattribute__(e))
        report_buffer.write(location["forecast"]["raw"]["forecast_keypoint"])
        report_buffer.write(location["forecast"]["raw"]["hourly"]["description"])
        return report_buffer.getvalue()


class RealTimeReporter(object):

    location = None

    @property
    def basic_info(self):
        tid = _config.config["units"]["temperature"]
        t_value = units.temperature_convert_to(self.location["temperature"], tid)
        t_name = units.unit_entries["temperature"]["choices"][tid]
        report = _("In {name} the weather is currently{temperature} degrees {unit}, {condition}")
        report = report.format(
            name=self.location["name"],
            temperature=t_value,
            unit=t_name,
            condition=self.location["sky_con"]
        )
        return report

    def report(self, location):
        self.location = location
        seq = _config.real_time_report_sequence()
        report_buffer = StringIO()
        for e in seq:
            report_buffer.write(self.__getattribute__(e))
        return report_buffer.getvalue()

