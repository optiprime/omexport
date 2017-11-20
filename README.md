# omexport -- Oruxmaps track exporter

## Introduction

This program I have written to export all of my Oruxmaps tracks as GPX files for further processing on GPSies.com and Google Earth. Oruxmaps is a great navigation app for the Android platform.

## Usage

Locate the file oruxmapstracks.db on your Android mobile and copy it to a temporary folder on your PC.
On your mobile phone, you usually find oruxmapstracks.db in /sdcard/oruxmaps. Open a command / shell window on your PC, "cd" to the temporary folder and call the python script omexport.py:

```bash
cd my_temporary_folder

python omexport.py
```

Alternatively specify the location of input database file and output track directory:

```bash
python omexport.py --database my/input-directory/oxuxmapstracks.db --tracks my/output-directory/tracks
````

## Requirements

```
git clone pip install gpxpy
```

## License
omexport is license under [MIT-License] (https://en.wikipedia.org/wiki/MIT_License)

