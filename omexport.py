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


class OmExport:
    "Oruxmaps track export"

    def __init__(self, database_file='oruxmapstracks.db', output_dir='tracks', output_file='tracks.gpx'):
        self.database_file = database_file
        self.output_dir = output_dir
        self.output_file = output_file

        self.database = sqlite3.connect(self.database_file)
        self.database.row_factory = sqlite3.Row


    def __del__(self):
        self.database.close()


    def write_individual_tracks(self):
        "Write all database tracks to individual GPX files in sub-folders"

        if not os.path.exists(self.output_dir):
            try:
                os.mkdir(self.output_dir)
            except OSError as ex:
                print("Fatal: Cannot create output directory {}: {}".format(self.output_dir, ex))
                return

        tracks = self.database.cursor()
        tracks.execute('''select _id, trackfolder, trackname, trackdescr from tracks
                          order by trackfolder, _id''')

        for row in tracks:
            track_id = row['_id']
            track_folder = row['trackfolder']
            track_name = row['trackname']
            track_description = row['trackdescr']

            print('Exporting track {} / {}'.format(track_folder, track_name))

            output_sub_dir = self.output_dir
            if not track_folder == '' and not track_folder == '---':
                output_sub_dir += '/' + sanitize_filename(track_folder)

            if not os.path.exists(output_sub_dir):
                try:
                    os.mkdir(output_sub_dir)
                except OSError:
                    # if track folder sub-directory cannot be created, use main output directory instead
                    output_sub_dir = self.output_dir

            gpx = gpxpy.gpx.GPX()
            self.add_track_to_gpx(track_id, track_name, track_description, gpx)

            filename = "{0}/{1:0>8}_{2}.gpx".format(output_sub_dir, track_id,
                                                    sanitize_filename(track_name))
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(gpx.to_xml())
            except OSError as ex:
                print('Error: Cannot write file {}: {} - using track-ID as name'.format(filename, ex))

                filename = "{0}/{1:0>8}.gpx".format(output_sub_dir, track_id)

                try:
                    with open(filename, 'w', encoding='utf-8') as file:
                        file.write(gpx.to_xml())
                except OSError as ex:
                    print('Error: Cannot write file {}: {} - skipping track.'.format(filename, ex))

        tracks.close()


    def write_combined_track(self):
        "Write all database tracks to one GPX file"

        gpx = gpxpy.gpx.GPX()

        tracks = self.database.cursor()
        tracks.execute('''select _id, trackfolder, trackname, trackdescr from tracks
                          order by trackfolder, _id''')

        for row in tracks:
            track_id = row['_id']
            track_name = row['trackname']
            track_description = row['trackdescr']
            track_folder = row['trackfolder']

            print('Exporting track {} / {}'.format(track_folder, track_name))

            if  not track_folder == '' and not track_folder == '---':
                track_name = '{} - {}'.format(track_folder, track_name)
            
            self.add_track_to_gpx(track_id, track_name, track_description, gpx)

        tracks.close()

        try:
            with open(self.output_file, 'w', encoding='utf-8') as file:
                file.write(gpx.to_xml())
        except OSError as ex:
            print('Error: Cannot write file {}: {} - using track-ID as name'.
                    format(self.output_file, ex))


    def add_track_to_gpx(self, track_id, track_name, track_description, gpx):
        "Reads track information from database and appends it to current GPX object"

        gpx_track = gpxpy.gpx.GPXTrack(name=track_name, description=track_description)
        gpx.tracks.append(gpx_track)

        segments = self.database.cursor()
        segments.execute('''select _id from segments
                            where segtrack = ?
                            order by _id''', (track_id,))

        points = self.database.cursor()

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


def main():
    "Main program"

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--combined',
                        default=False,
                        action='store_true',
                        help='write one GPX file containing all tracks instead of one GPX file for each track')
    parser.add_argument('--database',
                        default='oruxmapstracks.db',
                        help='the oruxmapstracks.db database file')
    parser.add_argument('--tracks',
                        default='tracks',
                        help='the output directory (if running in "individual" mode)')
    parser.add_argument('--track',
                        default='tracks.gpx',
                        help='the output track (if running in )')
    args = parser.parse_args()

    ome = OmExport(args.database, args.tracks, args.track)

    if args.combined:
        ome.write_combined_track()
    else:
        ome.write_individual_tracks()


if __name__ == "__main__":
    main()
