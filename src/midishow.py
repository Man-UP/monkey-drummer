#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from argparse import ArgumentParser
from pprint import pprint
import sys

import midi

def build_argument_parser():
    argument_parser = ArgumentParser()
    argument_parser.add_argument('midi_file')
    return argument_parser

def main(argv=None):
    if argv is None:
        argv = sys.argv
    argument_parser = build_argument_parser()
    arguments = argument_parser.parse_args(args=argv[1:])
    midi_file = midi.read_midifile(arguments.midi_file)
    for name, index in sorted(midi_file.tracknames.iteritems(),
                key=lambda item: item[1]):
        print('%2d %s' % (index, name))
        note_freq = {}
        for event in midi_file.tracklist[index]:
            if isinstance(event, midi.NoteOnEvent) and event.channel == 9:
                if event.channel not in note_freq:
                    note_freq[event.channel] = {}
                freq = note_freq[event.channel]
                if event.pitch not in freq:
                    freq[event.pitch] = 0
                freq[event.pitch] += 1
        print('Channel %d'% index)
        pprint(note_freq)

    return 0

if __name__ == '__main__':
    exit(main())

