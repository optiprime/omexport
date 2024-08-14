# omexport -- Oruxmaps track exporter

## Introduction

This program I have written to export all of my Oruxmaps tracks as GPX files for further processing on GPSies.com and Google Earth. Oruxmaps is a great navigation app for the Android platform.

## Usage

Locate the file /sdcard/oruxmaps/oruxmapstracks.db on your Android mobile and copy it to a temporary folder on your PC. Open a command or shell window on your PC, "cd" to the temporary folder and call the python script omexport.py.

### Writing individual GPX files, one for each track

```bash
cd my_temporary_folder

python omexport.py
```

Alternatively specify the location of input database file and output tracks directory:

```bash
python omexport.py --database my/input-directory/oxuxmapstracks.db --tracks my/output-directory/tracks
```

All Oruxmaps-tracks are exported to indvidual GPX files. The GPX files are named by their track name prefixed by their track ID. If you have made use of track folders in Oruxmaps, the output files are also organised in a folder structure. Using the option ```--folder-file``` you can write an additional GPX file (folder.gpx) for each folder, containing all tracks of this folder.

Waypoints related to tracks will also be included in the resulting GPX files.

### Writing one GPX file containing all tracks

```bash
cd my_temporary_folder

python omexport.py --combine
```

Alternatively specify the location of input database file and output GPX file:

```bash
python omexport.py --combine --database my/input-directory/oxuxmapstracks.db --track my_output_tracks.gpx
```

All Oruxmaps-tracks are exported to one GPX file. The GPX file contains a track list. Tracks are named by their track name prefixed by their track folder name (if available). This GPX file can be dragged and dropped to Google Earth.

## Requirements

Omexport is based on Python 3.X and the great GPXpy library: 

```bash
pip install gpxpy
```

## License

Omexport is licensed under [MIT-License](https://en.wikipedia.org/wiki/MIT_License)
