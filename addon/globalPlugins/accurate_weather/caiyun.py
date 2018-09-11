from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import json
from . import util
from . import base
from logHandler import log
import time
import uuid
import datetime
from . import units
import ui
import addonHandler

addonHandler.initTranslation()


class WeatherDataProvider(base.AbstractWeatherDataProvider):
    provider_id = 0

    name = _("Colorful Clouds")

    supported_realtime_entries = ["temperature",
                                  "sky_con",
                                  "pressure",
                                  "air_quality_index"]

    minutely_entries = []
    hourly_entries = []
    daily_entries = ["skycon", "skycon_20h_32h", "skycon_08h_20h"]
    daily_max_min_avg_entries = ["cloudrate", "aqi", "temperature", "humidity", "pres", "precipitation"]
    daily_index_entries = ["comfort", "ultraviolet", "dressing", "carWashing", "coldRisk"]

    minimum_interval = 5 * 60

    @property
    def temperature(self):
        """
        :return: int
        """
        return self.raw["result"]["temperature"]

    @property
    def pressure(self):
        return self.raw["result"]["pres"]

    @property
    def air_quality_index(self):
        return self.raw["result"]["aqi"]

    @property
    def sky_con(self):
        try:
            con = units.sky_con_dic[self.raw["result"]["skycon"]]
        except KeyError:
            con = self.raw["result"]["skycon"]
        return con

    @property
    def humidity(self):
        return self.raw["result"]["humidity"]

    @property
    def pm25(self):
        return self.raw["result"]["pm25"]

    @property
    def pm10(self):
        return self.raw["result"]["pm10"]

    @property
    def visibility(self):
        return self.raw["result"]["visibility"]

    @property
    def cloudrate(self):
        return self.raw["result"]["cloudrate"]

    @property
    def wind_speed(self):
        return self.raw["result"]["wind"]["speed"]

    @property
    def wind_direction(self):
        return self.raw["result"]["wind"]["direction"]

    def update(self, location):
        self.check_interval(location)
        weather_url = self.get_api_url(location)
        data = util.get_data_from_url(weather_url)
        self.raw = json.loads(data)
        if self.raw["status"] != "ok":
            ui.message(_("Quota exceeded please try tomorrow"))
            return None
        log.info(self.raw)
        for e in self.supported_realtime_entries:
            location[e] = self.__getattribute__(str(e))
        location["last_provider"] = self.provider_id

    def forecast_update(self, location):
        self.check_interval(location)
        weather_url = self.get_api_url(location, forecast=True)
        data = util.get_data_from_url(weather_url)
        self.raw_f = json.loads(data)
        if self.raw_f["status"] != "ok":
            ui.message(_("Quota exceeded please try tomorrow"))
            return None
        log.info(self.raw_f)
        location["forecast"] = {}
        location["forecast"]["raw"] = self.raw_f["result"]
        location["forecast"]["daily"] = {}
        for entry in self.daily_entries:
            for item in self.raw_f["result"]["daily"][entry]:
                try:
                    location["forecast"]["daily"][item["date"]][entry] = item["value"]
                except KeyError:
                    location["forecast"]["daily"][item["date"]] = {}
        for entry in self.daily_max_min_avg_entries:
            for item in self.raw_f["result"]["daily"][entry]:
                try:
                    location["forecast"]["daily"][item["date"]][entry]["max"] = item["max"]
                    location["forecast"]["daily"][item["date"]][entry]["min"] = item["min"]
                    location["forecast"]["daily"][item["date"]][entry]["avg"] = item["avg"]
                except KeyError:
                    location["forecast"]["daily"][item["date"]] = {}
        for entry in self.daily_index_entries:
            for item in self.raw_f["result"]["daily"][entry]:
                try:
                    location["forecast"]["daily"][item["datetime"]][entry]["desc"] = item["desc"]
                    location["forecast"]["daily"][item["datetime"]][entry]["index"] = item["index"]
                except KeyError:
                    location["forecast"]["daily"][item["datetime"]] = {}
        location["last_provider"] = self.provider_id

    def check_interval(self, location):
        now = time.time()
        try:
            update_time = location["last_update_time"]
            if update_time - now < self.minimum_interval:
                return False
        except KeyError:
            location["last_update_time"] = now
        return True

    def access_method(self):
        from . import _config
        return _config.cc_access_method()

    def get_proxy_token(self):
        return str(uuid.uuid1())

    def get_api_token(self):
        from . import _config
        return _config.cc_api_token()

    def get_proxy_base_url(self):
        from . import  _config
        return _config.cc_proxy_base_url()

    def get_api_url(self, location, forecast=False):
        am = self.access_method()
        if am == 0:
            realtime_tail = r"&type=realtime"
            forecast_tail = r"&type=forecast"
            location_string = r"&lon=" + location["longitude"] + r"&lat=" + location["latitude"]
            base_url = self.get_proxy_base_url() + self.get_proxy_token()
        elif am == 1:
            realtime_tail = "/realtime.json"
            forecast_tail = "/forecast.json"
            base_url = r"https://api.caiyunapp.com/v2/" + self.get_api_token()
            location_string = r'/' + location["longitude"] + ',' + location["latitude"]
        if forecast:
            return base_url + location_string + forecast_tail
        else:
            return base_url + location_string + realtime_tail

