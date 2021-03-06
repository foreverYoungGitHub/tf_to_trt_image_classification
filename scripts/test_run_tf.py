# Copyright (c) 2018, NVIDIA CORPORATION. All rights reserved.
# Full license terms provided in LICENSE.md file.

import sys
sys.path.append('third_party/models/')
sys.path.append('third_party/models/research')
sys.path.append('third_party/models/research/slim')
#from PIL import Image
#import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from model_meta import NETS, FROZEN_GRAPHS_DIR, CHECKPOINT_DIR
import time
import cv2
import gc

NUM_RUNS=50

if __name__ == '__main__':
    net_name = sys.argv[1]
    TEST_IMAGE_PATH = sys.argv[2]
    output_path = sys.argv[3]
    net_meta = NETS[net_name]

    with open(output_path, 'a') as test_f:
        print("Testing %s" % net_name)

        with tf.Graph().as_default() as graph:
            with open(net_meta['frozen_graph_filename'], 'rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
                tf.import_graph_def(graph_def, name="")
                graph_def = None
        
            tf_config = tf.ConfigProto()
            tf_config.gpu_options.allow_growth = True
            tf_config.allow_soft_placement = True

            tl0 = time.time()
            with tf.Session(config=tf_config, graph=graph) as tf_sess:
                tf_input = tf_sess.graph.get_tensor_by_name(net_meta['input_name'] + ':0')
                tf_output = tf_sess.graph.get_tensor_by_name(net_meta['output_names'][0] + ':0')
                tl1 = time.time()
                tldiff = 1000.0 * (tl1 - tl0)

                # load and preprocess image
                image = cv2.imread(TEST_IMAGE_PATH)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (net_meta['input_width'], net_meta['input_height']))
                image = net_meta['preprocess_fn'](image)

                # run network
                times = []
                for i in range(NUM_RUNS + 1):
                    t0 = time.time()
                    output = tf_sess.run([tf_output], feed_dict={
                        tf_input: image[None, ...]
                    })[0]
                    t1 = time.time()
                    times.append(1000.0 * (t1 - t0))
                avg_time = np.mean(times[1:]) # don't include first run

                # parse output
                top5 = net_meta['postprocess_fn'](output)
                print(top5)
                # test_f.write("%s %s %s\n" % (net_name, TEST_IMAGE_PATH, avg_time))
                # "Plan;File;AvgTimeMs;FPS;MemBytes"
                print >>test_f, "%s;%s;%f;%f;%d;%f" % (net_name, TEST_IMAGE_PATH, avg_time, 1000.0 / avg_time, -1, tldiff)
                test_f.flush() # cause of memory leaks no file is written

        # enforce garbage collector
        # tf.reset_default_graph()
        # gc.collect()
            
