from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from argparse import ArgumentParser
import os
import sys

from monkeydrummer import *
from monkeydrummer.graph import *
from monkeydrummer.io import *

def build_argument_parser():
    ap = ArgumentParser()
    add = ap.add_argument
    add('-c', '--channel', default=9, type=int)
    add('-g', '--graph')
    add('-l', '--length', default=256, type=int)
    add('-o', '--output')
    add('-r', '--order', default=16, type=int)
    add('-q', '--quantisation-level', default=16, type=int)
    add('-t', '--tempo', default=120, type=int)
    add('-v', '--velocity', default=100, type=int)
    add('midi_files', nargs='+')
    return ap

def main(argv=None):
    if argv is None:
        argv = sys.argv
    ap = build_argument_parser()
    args = ap.parse_args(args=argv[1:])

    args.quantisation_level = 1 / float(args.quantisation_level)

    trans = {}
    total = len(args.midi_files)
    for i, midi_file_path in enumerate(args.midi_files, start=1):
        print("Analysing '%s' (%d/%d)..."
              % (os.path.splitext(os.path.basename(midi_file_path))[0],
                 i, total), end='')
        sys.stdout.flush()
        try:
            track = read_midi_file(midi_file_path,
                channel=args.channel,
                quantisation_level=args.quantisation_level)
        except TypeError:
            print('failed')
        else:
            trans = make_trans_map(track, args.order, trans)
            print('done')

    print('Calculating markov model...', end='')
    sys.stdout.flush()
    probs = make_probs_map(trans)
    print('done')

    states = set()
    for from_state, to_states in probs.iteritems():
        states.add(from_state)
        for to_state in to_states:
            states.add(to_state)

    print('State space: %d' % len(states))

    if args.output:
        print('Generating sequence...', end='')
        sys.stdout.flush()
        seq = generate_sequence(probs, args.length)
        print('done')

        print("Writing MIDI file to '%s'..." % (args.output,), end='')
        sys.stdout.flush()
        write_midi_file(seq, args.output,
                duration=args.quantisation_level, tempo=args.tempo,
                velocity=args.velocity)
        print('done')

    if args.graph:
        print("Writing graph file to '%s'..." % (args.graph,), end='')
        sys.stdout.flush()
        write_graph(probs, args.graph)
        print('done')

    print('Goodbye!')
    return 0

if __name__ == '__main__':
    exit(main())
