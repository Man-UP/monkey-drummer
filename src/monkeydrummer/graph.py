from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pygraphviz import AGraph

__all__ = ('write_graph',)

def write_graph(probs, path):
    graph = AGraph(directed=True)
    next_label = 0
    labels = {}
    for from_state, to_states in probs.iteritems():
        if from_state not in labels:
            labels[from_state] = next_label
            next_label += 1
        for to_state in to_states:
            if to_state not in labels:
                labels[to_state] = next_label
                next_label += 1
    for label in xrange(next_label):
        graph.add_node(label, fillcolor='blue', label='', style='filled')
    for from_state, to_states in probs.iteritems():
        for to_state, prob in to_states.iteritems():
            graph.add_edge(labels[from_state], labels[to_state],
                           label='%.2g' % prob)
    # prog: neato (default), dot, twopi, circo, fdp or nop.
    graph.layout()
    graph.draw(path)

