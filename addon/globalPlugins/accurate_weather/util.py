import json
import ui
try:
    from urllib import urlopen
except ImportError:
    # Python 3
    from urllib.request import urlopen


def FindWoeID(lng, lat):
    base_url = r"https://query.yahooapis.com/v1/public/yql?q="
    yql = "select%20woeid%20from%20geo.places%20where%20text%3D%22({1},{0})%22%20limit%205&diagnostics=false&format=json".format(
        lng, lat)
    raw = get_data_from_url(base_url + yql)
    if raw:
        data = json.loads(raw)
    else:
        return None
    try:
        woeid = data["query"]["results"]["place"][0]["woeid"]
    except KeyError:
        woeid = None
    return woeid


# noinspection PyBroadException
def get_data_from_url(url):
    try:
        req = urlopen(url)
        data = req.read()
        data = data.decode(encoding="utf-8", errors="strict")
    except UnicodeDecodeError:
        return None
    except:
        ui.message(_("Network error occurred please check your Internet connection or firewall settings."))
        return 0
    return data


# class MyHTMLParser(HTMLParser):
#
#     def handle_starttag(self, tag, attrs):
#         print('<%s>' % tag)
#
#     def handle_endtag(self, tag):
#         print('</%s>' % tag)
#
#     def handle_startendtag(self, tag, attrs):
#         print('<%s/>' % tag)
#
#     def handle_data(self, data):
#         print(data)
#
#     def handle_comment(self, data):
#         print('<!--', data, '-->')
#
#     def handle_entityref(self, name):
#         print('&%s;' % name)
#
#     def handle_charref(self, name):
#         print('&#%s;' % name)
