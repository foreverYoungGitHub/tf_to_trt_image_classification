from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
sys.path.append('third_party/models/')
sys.path.append('third_party/models/research')
sys.path.append('third_party/models/research/slim')
import uff
from model_meta import NETS, FROZEN_GRAPHS_DIR, CHECKPOINT_DIR, PLAN_DIR
import os

import argparse
import sys

from tensorflow.core.framework import graph_pb2
from tensorflow.python.client import session
from tensorflow.python.framework import importer
from tensorflow.python.framework import ops
from tensorflow.python.platform import app
from tensorflow.python.platform import gfile
from tensorflow.python.summary import summary


def import_to_tensorboard(model_dir, log_dir):
  """View an imported protobuf model (`.pb` file) as a graph in Tensorboard.
  Args:
    model_dir: The location of the protobuf (`pb`) model to visualize
    log_dir: The location for the Tensorboard log to begin visualization from.
  Usage:
    Call this function with your model location and desired log directory.
    Launch Tensorboard by pointing it to the log directory.
    View your imported `.pb` model as a graph.
  """
  with session.Session(graph=ops.Graph()) as sess:
    with gfile.FastGFile(model_dir, "rb") as f:
      graph_def = graph_pb2.GraphDef()
      graph_def.ParseFromString(f.read())
      importer.import_graph_def(graph_def)

    pb_visual_writer = summary.FileWriter(log_dir)
    pb_visual_writer.add_graph(sess.graph)
    


if __name__ == '__main__':
    datatype = 'half'
    suffix = ''
    if len(sys.argv) > 1:
        suffix = "_" + sys.argv[1]
        datatype = sys.argv[1]
        
    if not os.path.exists('data/graphs'):
        os.makedirs('data/graphs')

    for net_name, net_meta in NETS.items():
        if 'exclude' in net_meta.keys() and net_meta['exclude'] is True:
            continue
        import_to_tensorboard(net_meta['frozen_graph_filename'], 'data/graphs/{}'.format())

    print("Model Imported. Visualize by running: "
          "tensorboard --logdir=data/graphs")
        