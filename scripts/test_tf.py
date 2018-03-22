from model_meta import NETS
import os, sys
import subprocess

TEST_OUTPUT_PATH='data/test_output_tf.csv'
PYTHON='/usr/bin/python'
TEST_SCRIPT=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_run_tf.py')
TEST_IMAGES_PATHS=['data/images/gordon_setter.jpg', 'data/images/lifeboat.jpg', 'data/images/golden_retriever.jpg']

if __name__ == '__main__':
    if len(sys.argv) > 1:
        TEST_OUTPUT_PATH = 'data/test_output_trt_%s.csv' % (sys.argv[1])
        print("Outputting to: %s" % TEST_OUTPUT_PATH)

    with open(TEST_OUTPUT_PATH, 'w') as test_f:
        print >>test_f, "Plan;File;AvgTimeMs;FPS;MemBytes"
        
    for net_name, net_meta in NETS.items():
        if 'exclude' in net_meta.keys() and net_meta['exclude'] is True:
            continue

        for TEST_IMAGE_PATH in TEST_IMAGES_PATHS:
            args = [
                net_name,
                TEST_IMAGE_PATH,
                TEST_OUTPUT_PATH
            ]
            print("Running %s" % net_name)
            subprocess.call([PYTHON, TEST_SCRIPT] + args)
