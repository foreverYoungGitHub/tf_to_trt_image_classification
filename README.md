TensorFlow -> TensorRT Image Classification
===

Original repository (with documentation): [here](https://github.com/NVIDIA-Jetson/tf_to_trt_image_classification).
This fork is for some timing and memory measurements.

## Setup

1. Flash the Jetson TX2 using JetPack 3.2.
   JetPack has a dhcp server configuration bug when Jetson isn't connected to a router.

2. Install pip on Jetson TX2.
    ```
    sudo apt-get install python-pip
    sudo pip install --upgrade pip
    sudo pip install --upgrade setuptools
    ```

3. Install TensorFlow on Jetson TX2.
   1. Download the TensorFlow 1.5.0 pip wheel from [here](https://drive.google.com/open?id=1ZYUJqcFdJytdMCQ5bVDtb3KoTqc_cugG). This build of TensorFlow is provided as a convenience for the purposes of this project.
   2. Install TensorFlow using pip
  
            sudo pip install tensorflow-1.5.0rc0-cp27-cp27mu-linux_aarch64.whl

4. Install uff exporter on Jetson TX2.
   1. Download TensorRT 3.0.4 for Ubuntu 16.04 and CUDA 9.0 tar package from https://developer.nvidia.com/nvidia-tensorrt-download.
   2. Extract archive 

            tar -xzf TensorRT-3.0.4.Ubuntu-16.04.3.x86_64.cuda-9.0.cudnn7.0.tar.gz

   3. Install uff python package using pip 

            sudo pip install TensorRT-3.0.4/uff/uff-0.2.0-py2.py3-none-any.whl

5. Clone and build this project

    ```
    git clone --recursive https://github.com/anwesender/tf_to_trt_image_classification.git
    cd tf_to_trt_image_classification
    mkdir build
    cd build
    cmake ..
    make 
    cd ..
    ```

## Download models and create frozen graphs

Run the following bash script to download all of the pretrained models. 

```
source scripts/download_images.sh
source scripts/download_models.sh
python scripts/models_to_frozen_graphs.py
```

## Benchmark all models

To benchmark all of the models, first convert all of the models that you downloaded above into TensorRT engines. Run the following script to convert all models

```
python scripts/frozen_graphs_to_plans.py
```

If you want to change parameters related to TensorRT optimization, just edit the [scripts/frozen_graphs_to_plans.py](scripts/frozen_graphs_to_plans.py) file.
Next, to benchmark all of the models run the [scripts/test_trt.py](scripts/test_trt.py) script

```
python scripts/test_trt.py
```

Once finished, the timing results will be stored at **data/test_output_trt.txt**.
If you want to also benchmark the TensorFlow models, simply run.

```
python scripts/test_tf.py
```

The results will be stored at **data/test_output_tf.txt**.

## Convert frozen graph to TensorRT engine

Run the [scripts/convert_plan.py](scripts/convert_plan.py) script from the root directory of the project, referencing the models table for relevant parameters.  For example, to convert the Inception V1 model run the following

```
python scripts/convert_plan.py data/frozen_graphs/inception_v1.pb data/plans/inception_v1.plan input 224 224 InceptionV1/Logits/SpatialSqueeze 1 0 float
```

The inputs to the convert_plan.py script are

1. frozen graph path
2. output plan path
3. input node name
4. input height
5. input width
6. output node name
7. max batch size
8. max workspace size
9. data type (float or half)

This script assumes single output single input image models, and may not work out of the box for models other than those in the table above.

<a name="execute"></a>
## Execute TensorRT engine

Call the [examples/classify_image](examples/classify_image) program from the root directory of the project, referencing the models table for relevant parameters.  For example, to run the Inception V1 model converted as above

```
./build/examples/classify_image/classify_image data/images/gordon_setter.jpg data/plans/inception_v1.plan data/imagenet_labels_1001.txt input InceptionV1/Logits/SpatialSqueeze inception
```

For reference, the inputs to the example program are

1. input image path
2. plan file path
3. labels file (one label per line, line number corresponds to index in output)
4. input node name
5. output node name
6. preprocessing function (either vgg or inception)

We provide two image label files in the [data folder](data/).  Some of the TensorFlow models were trained with an additional "background" class, causing the model to have 1001 outputs instead of 1000.  To determine the number of outputs for each model, reference the [NETS](scripts/model_meta.py#L67) variable in [scripts/model_meta.py](scripts/model_meta.py).
