#!/bin/bash

# cd build
# cmake ..
# make
# cd ..

TIME="/usr/bin/time --append -o data/timings.txt "

echo "32bit float"
if [ ! -f data/plans_f32.done ]; then
    echo "32bit float conversion" >> data/timings.txt 
    $TIME python scripts/frozen_graphs_to_plans.py float
    touch data/plans_f32.done
fi
echo "32bit float inference" >> data/timings.txt 
$TIME python scripts/test_trt.py float

echo "16bit float"
if [ ! -f data/plans_f16.done ]; then
    echo "16bit float conversion" >> data/timings.txt 
    $TIME python scripts/frozen_graphs_to_plans.py half
    touch data/plans_f16.done
fi
echo "16bit float inference" >> data/timings.txt 
$TIME python scripts/test_trt.py half

# echo "8bit integer"
# if [ ! -f data/plans_i8.done ]; then
#     echo "8bit integer conversion" >> data/timings.txt
#     $TIME python scripts/frozen_graphs_to_plans.py int8
#     touch data/plans_i8.done
# fi
# echo "8bit integer inference" >> data/timings.txt
# $TIME python scripts/test_trt.py int8

echo "tensorflow"
echo "tensorflow" >> data/timings.txt 
$TIME python scripts/test_tf.py

