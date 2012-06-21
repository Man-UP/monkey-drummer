from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import midi

from midiutil import MidiFile

__all__ = ('read_drum_file', 'read_midi_file', 'write_midi_file')

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

