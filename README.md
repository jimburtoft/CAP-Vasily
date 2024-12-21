# CAP-Vasily

This application is made to convert .kml files from the Waldo mission planning process into a flightlines.txt file that has points that can be loaded into foreflight, and an .fpl file that can be loaded into a Garmin G1000 system.

This application will extract the GPS coordinates of each line in the mission, as well as giving you options to reorder or add additional points that may aid in the flying or tracking of the mission.

Refer to internal documentation for more information about how to use this application.

# Instructions

The easiest way to use this program is to download the latest .exe from the Releases tab.

[The latest release.](https://github.com/jimburtoft/CAP-Vasily/releases)

If you want to build from source:
Install python and create a virtual environment.
```
git clone https://github.com/jimburtoft/CAP-Vasily.git
cd CAP-Vasily
pip install -r requirements.txt
pyinstaller "CAP Waldo Flightline Converter.spec"
```

# Personal Project
This is a personal project and is neither affiliated with nor approved by the Civil Air Patrol.
