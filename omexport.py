#! /usr/bin/env python

"""
Export Oruxmaps tracks to GPX files

MIT License

Copyright (c) 2017 https://github.com/optiprime

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import datetime
import sqlite3
import gpxpy
import gpxpy.gpx

def sanitize_filename(string):
    "Replaces illegal characters in filename"

    return string.replace('/', '--').replace('\\', '--').replace(
        ':', '-').replace('\r', ' ').replace('\n', ' ').replace('*', '+')

def write_track(database, track_id, track_folder, track_name, track_description, output_dir):
    "Writing GPX track to output file in output folder"

    output_sub_dir = output_dir
    if not track_folder == '' and not track_folder == '---':
        output_sub_dir += '/' + sanitize_filename(track_folder)

    if not os.path.exists(output_sub_dir):
        try:
            os.mkdir(output_sub_dir)
        except OSError:
            # if track folder sub-directory cannot be created, use main output directory instead
            output_sub_dir = output_dir

    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack(name=track_name, description=track_description)
    gpx.tracks.append(gpx_track)

    segments = database.cursor()
    segments.execute('''select _id from segments
                        where segtrack = ?
                        order by _id''', (track_id,))

    points = database.cursor()

    for segment_row in segments:
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        points.execute('''select trkptlat, trkptlon, trkptalt, trkpttime from trackpoints
                          where trkptseg = ?
                          order by _id''', (segment_row['_id'],))

        for point_row in points:
            gpx_segment.points.append(
                gpxpy.gpx.GPXTrackPoint(
                    point_row['trkptlat'], point_row['trkptlon'],
                    elevation=point_row['trkptalt'],
                    time=datetime.datetime.fromtimestamp(point_row['trkpttime'] / 1000.0)))

    points.close()
    segments.close()

    filename = "{0}/{1:0>8}_{2}.gpx".format(output_sub_dir, track_id, sanitize_filename(track_name))

    try:
        with open(filename, 'w') as file:
            file.write(gpx.to_xml())
    except OSError as ex:
        print('Error: Cannot write file {}: {} - using track-ID as name'.format(filename, ex))

        filename = "{0}/{1:0>8}.gpx".format(output_sub_dir, track_id)

        try:
            with open(filename, 'w') as file:
                file.write(gpx.to_xml())
        except OSError as ex:
            print('Error: Cannot write file {}: {} - skipping track.'.format(filename, ex))

def write_database_tracks(database_file, output_dir):
    "Write all database tracks to individual GPX files in sub-folders"

    if not os.path.exists(output_dir):
        try:
            os.mkdir(output_dir)
        except OSError as ex:
            print("Fatal: Cannot create output directory {}: {}".format(output_dir, ex))
            return

    database = sqlite3.connect(database_file)
    database.row_factory = sqlite3.Row

    tracks = database.cursor()
    tracks.execute('select _id, trackfolder, trackname, trackdescr from tracks')

    for row in tracks:
        print('Exporting track {} - {}'.format(row['_id'], row['trackname']))

        write_track(database, row['_id'], row['trackfolder'], row['trackname'],
                    row['trackdescr'], output_dir)

    tracks.close()

    database.close()

def main():
    "Main program"

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--database',
                        default='oruxmapstracks.db',
                        help='the oruxmapstracks.db database file')
    parser.add_argument('--tracks',
                        default='tracks',
                        help='the output directory (will be created if non-existing)')
    args = parser.parse_args()

    write_database_tracks(args.database, args.tracks)

if __name__ == "__main__":
    main()
