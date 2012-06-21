from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from copy import deepcopy
from itertools import chain
from random import random

import os
import sys

__all__ = ('make_trans_map', 'make_probs_map', 'generate_sequence')

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

