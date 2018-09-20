FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04

MAINTAINER Shawn Chen <kertansul@gmail.com>


################
### Settings ###
################

# Tensorflow
ARG TF_BRANCH=v1.11.0-rc1
ARG BAZEL_VERSION=0.15.0
ARG TF_AVAILABLE_CPUS=32
# Keras
ARG KERAS_APPLICATIONS=1.0.4
ARG KERAS_PREPROCESSING=1.0.2
# PyTorch(Caffe2)
ARG PYTORCH_TAG=v0.4.1
ARG BUILD_CAFFE2=1
ARG PYTORCH_VISION_TAG=v0.2.1
# nvidia Caffe
ARG CAFFE_BRANCH=caffe-0.17


############################
### Python 3.5 & OpenCV3 ###
############################

# For convenience, alisas (but don't sym-link) python & pip to python3 & pip3 as recommended in:
# http://askubuntu.com/questions/351318/changing-symlink-python-to-python3-causes-problems
RUN apt-get update && apt-get install -y --no-install-recommends python3.5 python3.5-dev python3-pip
RUN pip3 install --no-cache-dir --upgrade pip setuptools
RUN echo "alias python='python3'" >> /root/.bash_aliases
RUN echo "alias pip='pip3'" >> /root/.bash_aliases
RUN /bin/bash -c "source /root/.bash_aliases"
# Install OpenCV3
RUN pip3 install opencv-python


########################
### Build Tensorflow ###
########################

# modified from https://raw.githubusercontent.com/tensorflow/tensorflow/master/tensorflow/tools/docker/Dockerfile.devel-gpu-cuda9-cudnn7
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libnccl2=2.2.13-1+cuda9.0 \
        libnccl-dev=2.2.13-1+cuda9.0 \
        libcurl3-dev \
        libfreetype6-dev \
        libhdf5-serial-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        python3.5-dev \
        rsync \
        software-properties-common \
        unzip \
        zip \
        zlib1g-dev \
        wget \
        && \
    rm -rf /var/lib/apt/lists/* && \
    find /usr/local/cuda-9.0/lib64/ -type f -name 'lib*_static.a' -not -name 'libcudart_static.a' -delete && \
    rm /usr/lib/x86_64-linux-gnu/libcudnn_static_v7.a

RUN apt-get update && \
        apt-get install nvinfer-runtime-trt-repo-ubuntu1604-4.0.1-ga-cuda9.0 && \
        apt-get update && \
        apt-get install libnvinfer4=4.1.2-1+cuda9.0 && \
        apt-get install libnvinfer-dev=4.1.2-1+cuda9.0

# Link NCCL libray and header where the build script expects them.
RUN mkdir /usr/local/cuda-9.0/lib &&  \
    ln -s /usr/lib/x86_64-linux-gnu/libnccl.so.2 /usr/local/cuda/lib/libnccl.so.2 && \
    ln -s /usr/include/nccl.h /usr/local/cuda/include/nccl.h

RUN curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py

RUN pip3 --no-cache-dir install \
        Pillow \
        h5py \
        ipykernel \
        jupyter \
        keras_applications==$KERAS_APPLICATIONS \
        keras_preprocessing==$KERAS_PREPROCESSING \
        matplotlib \
        mock \
        numpy \
        scipy \
        sklearn \
        pandas \
        && \
    python3 -m ipykernel.kernelspec

# link python to python3
RUN ln -s -f /usr/bin/python3 /usr/bin/python

# notebook setup will be left in the last section #

# Set up Bazel.
# Running bazel inside a `docker build` command causes trouble, cf:
#   https://github.com/bazelbuild/bazel/issues/134
# The easiest solution is to set up a bazelrc file forcing --batch.
RUN echo "startup --batch" >>/etc/bazel.bazelrc
# Similarly, we need to workaround sandboxing issues:
#   https://github.com/bazelbuild/bazel/issues/418
RUN echo "build --spawn_strategy=standalone --genrule_strategy=standalone" \
    >>/etc/bazel.bazelrc
WORKDIR /
RUN mkdir /bazel && \
    cd /bazel && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -O https://github.com/bazelbuild/bazel/releases/download/$BAZEL_VERSION/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -o /bazel/LICENSE.txt https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE && \
    chmod +x bazel-*.sh && \
    ./bazel-$BAZEL_VERSION-installer-linux-x86_64.sh
# bazel cleanup
RUN cd / && \
    rm -f bazel/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    rm -rf /bazel

# Download and build TensorFlow.
WORKDIR /root/
RUN git clone https://github.com/tensorflow/tensorflow.git && \
    cd tensorflow && \
    git checkout ${TF_BRANCH}
WORKDIR /root/tensorflow

# Configure the build for our CUDA configuration.
ENV CI_BUILD_PYTHON python3
ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:$LD_LIBRARY_PATH
ENV TF_NEED_CUDA 1
ENV TF_CUDA_COMPUTE_CAPABILITIES=3.0,3.5,5.2,6.0,6.1
ENV TF_CUDA_VERSION=9.0
ENV TF_CUDNN_VERSION=7

# Build and Install TensorFlow.
RUN ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64/stubs:${LD_LIBRARY_PATH} \
    tensorflow/tools/ci_build/builds/configured GPU \
    bazel build -c opt --config=cuda \
        --cxxopt="-D_GLIBCXX_USE_CXX11_ABI=0" \
        tensorflow/tools/pip_package:build_pip_package && \
    rm /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/pip3 && \
    pip3 --no-cache-dir install --upgrade /tmp/pip3/tensorflow-*.whl
# Clean up pip wheel and Bazel cache when done.
RUN rm -rf /pip_pkg && \
    rm -rf /root/.cache/pip

# Install google pprof (for Profiler visualization)
RUN apt-get update && apt-get install -y graphviz
RUN pip3 --no-cache-dir install GraphViz
RUN cd ~ && curl -O https://dl.google.com/go/go1.10.2.linux-amd64.tar.gz && \
    tar xvf go1.10.2.linux-amd64.tar.gz && \
    mv go /usr/local && \
    rm go1.10.2.linux-amd64.tar.gz
ENV GOPATH=/root/go
ENV PATH=/usr/local/go/bin:$GOPATH/bin:$PATH
RUN go get github.com/google/pprof

# Expose Ports for TensorBoard (6006), Ipython (8888)
EXPOSE 6006 8888


################################
### Install Pytorch / Caffe2 ###
################################

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        libgoogle-glog-dev \
        libgtest-dev \
        libiomp-dev \
        libleveldb-dev \
        liblmdb-dev \
        libopencv-dev \
        libopenmpi-dev \
        libsnappy-dev \
        libprotobuf-dev \
        libgflags-dev \ 
        openmpi-bin \
        openmpi-doc \
        protobuf-compiler \
        python3.5-dev \
        python3-pip                          
RUN pip3 install \
        future \
        numpy \
        pyyaml \
        protobuf
RUN git clone --branch ${PYTORCH_TAG} https://github.com/pytorch/pytorch.git /root/pytorch 
WORKDIR /root/pytorch
RUN git submodule update --init --recursive
RUN ln -s -f /usr/bin/python3 /usr/bin/python
RUN FULL_CAFFE2=$BUILD_CAFFE2 python3 setup.py install

# Install torchvision
RUN git clone --branch ${PYTORCH_VISION_TAG} https://github.com/pytorch/vision.git /root/pytorch_vision
WORKDIR /root/pytorch_vision
RUN python3 setup.py install


##########################
### Build nvidia Caffe ###
##########################

# Install dependencies for Caffe
# some of the installations might be duplicated, but I just leave it there
RUN apt-get update && apt-get install -y \
        cmake \
        libatlas-base-dev \
        libboost-all-dev \
        libgflags-dev \
        libgoogle-glog-dev \
        libhdf5-serial-dev \
        libleveldb-dev \
        liblmdb-dev \
        libopencv-dev \
        libprotobuf-dev \
        libsnappy-dev \
        protobuf-compiler \
        libturbojpeg \
        && \
    rm -rf /var/lib/apt/lists/*

# Install Caffe 
RUN git clone -b ${CAFFE_BRANCH} --depth 1 https://github.com/NVIDIA/caffe.git /root/caffe && \
    cd /root/caffe && \
    cat python/requirements.txt | xargs -n1 pip3 install
RUN cd /root/caffe && \
    mkdir build && cd build && \
    cmake -DCUDA_ARCH_NAME="Manual" -DCUDA_ARCH_BIN="52 60" -DCUDA_ARCH_PTX="60" \
          -DUSE_CUDNN=1 -USE_NCCL=On -DBLAS=atlas -Dpython_version=3 .. && \
    make -j"$(nproc)" all && \
    make install

# Set up Caffe environment variables
ENV CAFFE_ROOT=/root/caffe
ENV PYCAFFE_ROOT=$CAFFE_ROOT/python
ENV PYTHONPATH=$PYCAFFE_ROOT:$PYTHONPATH \
    PATH=$CAFFE_ROOT/build/tools:$PYCAFFE_ROOT:$PATH

RUN echo "$CAFFE_ROOT/build/lib" >> /etc/ld.so.conf.d/caffe.conf && ldconfig


##############################################
#### Other utilities and environment setup ###
##############################################
WORKDIR /root

# Set up notebook config
COPY jupyter_notebook_config.py /root/.jupyter/

# Jupyter has issues with being run directly: https://github.com/ipython/ipython/issues/7062
COPY run_jupyter.sh /root/

# Vim and Bash Settings
RUN add-apt-repository -y ppa:jonathonf/vim && \
    apt-get update && apt-get install -y vim
COPY .bashrc /root
COPY .vimrc /root
COPY vimrc /etc/vim
RUN git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
RUN vim +PluginInstall +qall
RUN cd ~/.vim/bundle/YouCompleteMe && ./install.py --clang-completer
RUN cd ~/.vim/bundle/vim-colorschemes/ && cp -r colors ~/.vim/

# install less for better git log/diff displays
RUN apt-get install -y less
