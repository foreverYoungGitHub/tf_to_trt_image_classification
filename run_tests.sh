#!/bin/bash

cd build
cmake ..
make
cd ..

TIME="/usr/bin/time --append -o data/timings.txt "

echo "32bit float"
echo "32bit float conversion" >> data/timings.txt 
$TIME python scripts/frozen_graphs_to_plans.py float
echo "32bit float inference" >> data/timings.txt 
$TIME python scripts/test_trt.py float

echo "16bit float"
echo "16bit float conversion" >> data/timings.txt 
$TIME python scripts/frozen_graphs_to_plans.py half
echo "16bit float inference" >> data/timings.txt 
$TIME python scripts/test_trt.py half

echo "8bit integer"
echo "8bit integer conversion" >> data/timings.txt
$TIME python scripts/frozen_graphs_to_plans.py int8
echo "8bit integer inference" >> data/timings.txt
$TIME python scripts/test_trt.py int8

echo "tensorflow"
echo "tensorflow" >> data/timings.txt 
$TIME python scripts/test_tf.py

