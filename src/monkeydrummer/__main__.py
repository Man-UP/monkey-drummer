from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from argparse import ArgumentParser
import os
import sys

from monkeydrummer import *
from monkeydrummer.io import *

def build_argument_parser():
    ap = ArgumentParser()
    add = ap.add_argument
    add('-c', '--channel', default=9, type=int)
    add('-l', '--length', default=256, type=int)
    add('-o', '--output', default=os.path.expanduser('~/output.mid'))
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
    for midi_file_path in args.midi_files:
        print('%s...' % midi_file_path, end='')
        track = read_midi_file(midi_file_path,
            channel=args.channel, quantisation_level=args.quantisation_level)
        trans = make_trans_map(track, args.order, trans)
        print('done')
    probs = make_probs_map(trans)
    seq = generate_sequence(probs, args.length)
    write_midi_file(seq, args.output,
            duration=args.quantisation_level, tempo=args.tempo,
            velocity=args.velocity)
    print('Goodbye!')

if __name__ == '__main__':
    exit(main())
