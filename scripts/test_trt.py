# Copyright (c) 2018, NVIDIA CORPORATION. All rights reserved.
# Full license terms provided in LICENSE.md file.

import sys
#sys.path.append("../scripts")
#sys.path.append(".")
from model_meta import NETS
import os
import subprocess

# TEST_IMAGE_PATH='data/images/gordon_setter.jpg'
TEST_IMAGES_PATHS=['data/images/gordon_setter.jpg', 'data/images/lifeboat.jpg', 'data/images/golden_retriever.jpg']
TEST_OUTPUT_PATH='data/test_output_trt.csv'
TEST_EXE_PATH='./build/src/test/test_trt'

if __name__ == '__main__':
    suffix = ''
    if len(sys.argv) > 1:
        TEST_OUTPUT_PATH = 'data/test_output_trt_%s.csv' % (sys.argv[1])
        suffix = "_" + sys.argv[1]
        print("Outputting to: %s" % TEST_OUTPUT_PATH)
    
    # delete output file 
    #if os.path.isfile(TEST_OUTPUT_PATH):
    #   os.remove(TEST_OUTPUT_PATH)
    with open(TEST_OUTPUT_PATH, 'w') as test_f:
        print >>test_f, "Plan;File;AvgTimeMs;FPS;MemBytes;InitGraph"

    for net_name, net_meta in NETS.items():
        if 'exclude' in net_meta.keys() and net_meta['exclude'] is True:
            continue

        for TEST_IMAGE_PATH in TEST_IMAGES_PATHS:
            args = [
                TEST_IMAGE_PATH,
                net_meta['plan_filename'] + suffix,
                net_meta['input_name'],
                str(net_meta['input_height']),
                str(net_meta['input_width']),
                net_meta['output_names'][0],
                str(net_meta['num_classes']), 
                net_meta['preprocess_fn'].__name__,
                str(50), # numRuns
                "half", # dataType 
                str(1), # maxBatchSize 
                str(1 << 20), # workspaceSize 
                str(0), # useMappedMemory 
                TEST_OUTPUT_PATH
            ]
            print("Running %s" % net_name)
            subprocess.call([TEST_EXE_PATH] + args)
