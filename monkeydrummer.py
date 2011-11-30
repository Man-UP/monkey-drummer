#!/usr/bin/env python2.7
from __future__ import division
from __future__ import print_function
from copy import deepcopy
from itertools import chain
from random import random

from pygame import midi

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

def get_start_state(order):
    return tuple(None for _ in xrange(order))

def make_trans_map(track, order=1):
    current_state = get_start_state(order)
    trans = {}
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
        to_states = probs[current_state]
        r = random()
        cum_prob = 0
        for to_state, prob in to_states.iteritems():
            cum_prob += prob
            if cum_prob >= r:
                seq.append(to_state[-1])
                current_state = to_state
                break
    return seq    

def make_midi_events(seq, beat_duration, start_time, velocity=127):
    time = start_time
    events = []
    for beat in seq:
        for drum in beat:
            events.append(((0x99, drum, velocity), time))
        time += beat_duration
    return events

def main():
    track = read_drum_file('test.drm')
    trans = make_trans_map(track, 1)
    probs = make_probs_map(trans)
    seq = generate_sequence(probs, 256)

    midi.init()
    events = make_midi_events(seq, 250, midi.time()) 
    
    out = midi.Output(device_id=2, latency=1000)
    out.write(events)
    raw_input('hit return to exit')

if __name__ == '__main__':
    exit(main())
