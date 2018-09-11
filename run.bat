"C:\Program Files (x86)\NVDA\nvda.exe" --check-running
if errorlevel 1 (
"C:\Program Files (x86)\NVDA\nvda_slave.exe" launchNVDA -r
)
scons -c && scons && .\accurate_weather-0.1.0-dev.nvda-addon
