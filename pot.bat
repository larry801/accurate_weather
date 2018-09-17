del accurate_weather.pot && del readme.pot && scons pot && msgmerge -U  addon\locale\zh_CN\LC_MESSAGES\nvda.po accurate_weather.pot && node C:\Users\John\AppData\Roaming\npm\node_modules\gettext-markdown\bin\gettext-md.js -o readme.pot --pot ./addon/doc/en/readme.md

