from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from io import open
import json
import os
import globalVars

code_to_geo_dict = {}

province_list = None

level2_list = None

level3_list = None

level4_list = None


def load_region_code():
    global code_to_geo_dict, province_list
    code_path = os.path.join(globalVars.appArgs.configPath,
                             "addons",
                             "accurate_weather",
                             'code.js')
    with open(code_path, encoding='utf-8') as f:
        data = f.read()
        province_list = json.loads(data)
        region_path = os.path.join(globalVars.appArgs.configPath,
                                   "addons",
                                   "accurate_weather",
                                   'region.json')
    with open(region_path, encoding='utf-8') as f:
        code_to_geo_dict = json.load(f)
