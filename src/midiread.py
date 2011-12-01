#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from argparse import ArgumentParser, FileType
import sys

import midi

def read_midi_file(midi_path, track_index, quantisation_level=1/16):
    midi_file = midi.read_midifile(midi_path)
    # tick beat^-1 = (tick quart^-1 * quart note^-1) / note beat^-1
    tpb = 4 * midi_file.resolution *  quantisation_level
    midi_track = midi_file.tracklist[track_index]
    beats = {}
    for event in midi_track:
        if isinstance(event, midi.NoteOnEvent):
            beat_index = int(round(event.tick / tpb))
            print(tpb)
            if beat_index not in beats:
                beats[beat_index] = set()
            beats[beat_index].add(event.pitch)
    track = [frozenset() for _ in xrange(max(beats) + 1)]
    for beat_index, beat in beats.iteritems():
        track[beat_index] = frozenset(beat)
    return tuple(track)

def build_argument_parser():
    argument_parser = ArgumentParser()
    argument_parser.add_argument('input')
    argument_parser.add_argument('track_index', type=int)
    return argument_parser

def main(argv=None):
    if argv is None:
        argv = sys.argv
    argument_parser = build_argument_parser()
    arguments = argument_parser.parse_args(args=argv[1:])
    print(read_midi_file(arguments.input, arguments.track_index))
    return 0

if __name__ == '__main__':
    exit(main())

