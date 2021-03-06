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

## Jetson build Tensorflow from source

```
# prerequisits
sudo apt-get install -y openjdk-8-jdk zip unzip autoconf automake libtool curl python-numpy swig python-dev python-pip python-six python-wheel build-essential

# bazel
mkdir bazel
wget --no-check-certificate https://github.com/bazelbuild/bazel/releases/download/0.11.1/bazel-0.11.1-dist.zip
unzip bazel-0.11.1-dist.zip -d bazel-0.11.1-dist
cd bazel-0.11.1-dist
./compile.sh
sudo cp output/bazel /usr/local/bin
cd ../..

# tensorflow
git clone https://github.com/tensorflow/tensorflow
cd tensorflow
git checkout r1.7
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/extras/CUPTI/lib64
# checkout tensorrt_configure from current master branch because r1.7 didn't have the aarch64 switch
git checkout master -- third_party/tensorrt/tensorrt_configure.bzl
TF_NEED_KAFKA=0 TF_NEED_GCP=0 TF_NEED_OPENCL=0 TF_NEED_S3=0 TF_NEED_GCP=0 TF_NEED_HDFS=0 TF_NEED_CUDA=1 TF_CUDA_VERSION=9.0 CUDA_TOOLKIT_PATH=/usr/local/cuda TF_CUDNN_VERSION=7.0.5 CUDNN_INSTALL_PATH=/usr/lib/aarch64-linux-gnu/ TF_CUDA_COMPUTE_CAPABILITIES=6.2 CC_OPT_FLAGS=-march=native TF_NEED_JEMALLOC=1 TF_NEED_OPENCL=0 TF_ENABLE_XLA=0 TF_NEED_MKL=0 TF_NEED_MPI=0 TF_NEED_VERBS=0 TF_CUDA_CLANG=0 TF_NEED_TENSORRT=1 TENSORRT_INSTALL_PATH=/usr/lib/aarch64-linux-gnu ./configure
# press enter some times
bazel build --config=opt --config=cuda //tensorflow/tools/pip_package:build_pip_package
bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg
sudo pip install /tmp/tensorflow_pkg/tensorflow-1.7.0rc1-cp27-cp27mu-linux_aarch64.whl
```

## Ubuntu desktop setup

```
sudo dpkg -i cuda-repo-ubuntu1604_9.0.176-1_amd64.deb nv-tensorrt-repo-ubuntu1604-ga-cuda9.0-trt3.0.4-20180208_1-1_amd64.deb
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
sudo apt-get update
sudo apt-get install -y cuda-9.0
sudo dpkg -i cuda-repo-ubuntu1604_9.0.176-1_amd64.deb libcudnn7-doc_7.1.1.5-1+cuda9.0_amd64.deb libcudnn7-dev_7.1.1.5-1+cuda9.0_amd64.deb libcudnn7_7.1.1.5-1+cuda9.0_amd64.deb nv-tensorrt-repo-ubuntu1604-ga-cuda9.0-trt3.0.4-20180208_1-1_amd64.deb
sudo apt-get install tensorrt python-libnvinfer-doc python3-libnvinfer-doc uff-converter-tf
# install tensorflow: https://www.tensorflow.org/install/install_sources
```
