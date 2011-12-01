#!/usr/bin/env python2.7
from __future__ import division
from __future__ import print_function
from argparse import ArgumentParser
from copy import deepcopy
from itertools import chain
from random import random
import os
import sys

import midi

from midiutil import MidiFile

def get_start_state(order):
    return tuple(None for _ in xrange(order))

def make_trans_map(track, order=1, trans=None):
    current_state = get_start_state(order)
    trans = {} if trans is None else trans
    for beat in track:
        next_state = tuple(b for b in chain(current_state[1:], (beat,)))
        if current_state not in trans:
            trans[current_state] = {}
        to_states = trans[current_state]
        if next_state not in to_states:
            to_states[next_state] = 0
        to_states[next_state] += 1
        current_state = next_state
    return trans

def make_probs_map(trans):
    probs = deepcopy(trans)
    for to_states in probs.itervalues():
        total_freq = sum(to_states.itervalues())
        for to_state, freq in to_states.iteritems():
            to_states[to_state] = freq / total_freq
    return probs

def generate_sequence(probs, length):
    current_state = get_start_state(len(next(probs.iterkeys())))
    seq = []
    for _ in xrange(length):
        try:
            to_states = probs[current_state]
        except KeyError:
            break
        r = random()
        cum_prob = 0
        for to_state, prob in to_states.iteritems():
            cum_prob += prob
            if cum_prob >= r:
                seq.append(to_state[-1])
                current_state = to_state
                break
    return seq

def read_drum_file(path):
    with open(path) as drum_file:
        first_line = next(drum_file).strip()
        # - 3 to account for MIDI note number
        track = [set() for _ in xrange(len(first_line) - 3)]
        # stick the first line back on the file
        for line in chain((first_line,), drum_file):
            line = line.strip()
            drum_note = int(line[:3])
            for i, hit in enumerate(line[3:]):
                if hit == 'x':
                    track[i].add(drum_note)
    return map(frozenset, track)

def read_midi_file(midi_path, channel=9, quantisation_level=1/16):
    midi_file = midi.read_midifile(midi_path)

    # Find the drum tracks
    drum_tracks = set()
    for index, track in midi_file.tracklist.iteritems():
        for event in track:
            if isinstance(event, midi.NoteEvent) and event.channel == 9:
                drum_tracks.add(index)
                break

    # tick beat^-1 = (tick quart^-1 * quart note^-1) / note beat^-1
    tpb = 4 * midi_file.resolution *  quantisation_level
    beats = {}
    for track_index in drum_tracks:
        midi_track = midi_file.tracklist[track_index]
        for event in midi_track:
            if isinstance(event, midi.NoteOnEvent) and event.channel == channel:
                beat_index = int(round(event.tick / tpb))
                if beat_index not in beats:
                    beats[beat_index] = set()
                beats[beat_index].add(event.pitch)
    if beats:
        track = [frozenset() for _ in xrange(max(beats) + 1)]
        for beat_index, beat in beats.iteritems():
            track[beat_index] = frozenset(beat)
    return tuple(track)

def write_midi_file(seq, file_path, duration=1/16, tempo=120,
        velocity=100):
    midi_file = MidiFile.MIDIFile(1)
    midi_file.addTrackName(0, 0, 'Drums')
    midi_file.addTempo(0, 0, tempo)
    duration *= 4
    start = 0
    for beat in seq:
        for drum in beat:
            midi_file.addNote(0, 9, drum, start, duration, velocity)
        start += duration
    with open(file_path, 'wb') as midi_output_file:
        midi_file.writeFile(midi_output_file)

def build_argument_parser():
    ap = ArgumentParser()
    add = ap.add_argument
    add('-c', '--channel', default=9, type=int)
    add('-l', '--length', default=256, type=int)
    add('-o', '--output_midi_path', default=os.path.expanduser('~/output.mid'))
    add('-r', '--order', default=16, type=int)
    add('-q', '--quantisation-level', default=16, type=int)
    add('-t', '--tempo', default=120, type=int)
    add('-v', '--velocity', default=100, type=int)
    add('input_midi_path', nargs='+')
    return ap

def main(argv=None):
    if argv is None:
        argv = sys.argv
    ap = build_argument_parser()
    args = ap.parse_args(args=argv[1:])
    args.quantisation_level = 1 / float(args.quantisation_level)
    trans = {}
    for midi_file_path in args.input_midi_path:
        print('%s...' % midi_file_path, end='')
        track = read_midi_file(midi_file_path,
            channel=args.channel, quantisation_level=args.quantisation_level)
        trans = make_trans_map(track, args.order, trans)
        print('done')
    probs = make_probs_map(trans)
    seq = generate_sequence(probs, args.length)
    write_midi_file(seq, args.output_midi_path,
            duration=args.quantisation_level, tempo=args.tempo,
            velocity=args.velocity)

if __name__ == '__main__':
    exit(main())
