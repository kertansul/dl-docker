FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04

MAINTAINER Shawn Chen <kertansul@gmail.com>


################
### Settings ###
################
ARG TF_VERSION=2.0.0
ARG TORCH_VERSION=1.2.0
ARG TORCHV_VERSION=0.4.0


##################
### Python 3.6 ###
##################

# For convenience, alisas (but don't sym-link) python & pip to python3 & pip3 as recommended in:
# http://askubuntu.com/questions/351318/changing-symlink-python-to-python3-causes-problems
RUN apt-get update && apt-get install -y --no-install-recommends python3.6 python3.6-dev python3-pip
RUN pip3 install --no-cache-dir --upgrade pip setuptools
RUN echo "alias python='python3'" >> /root/.bash_aliases
RUN echo "alias pip='pip3'" >> /root/.bash_aliases
RUN /bin/bash -c "source /root/.bash_aliases"
# link python to python3
RUN ln -s -f /usr/bin/python3 /usr/bin/python


########################
### Build Tensorflow ###
########################

RUN pip3 --no-cache-dir install tensorflow-gpu==$TF_VERSION
# notebook setup will be left in the last section #


################################
### Install Pytorch / Caffe2 ###
################################

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        protobuf-compiler
RUN pip3 install torch==$TORCH_VERSION torchvision==$TORCHV_VERSION


##############################################
#### Other utilities and environment setup ###
##############################################
WORKDIR /root

# Install OpenCV
RUN apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender-dev
RUN pip3 install opencv-python

# Set up notebook config
COPY jupyter_notebook_config.py3 /root/.jupyter/jupyter_notebook_config.py

# Jupyter has issues with being run directly: https://github.com/ipython/ipython/issues/7062
COPY run_jupyter.sh /root/

# Vim and Bash Settings
RUN apt-get update && apt-get install -y vim
COPY .bashrc /root
COPY .vimrc /root
COPY vimrc /etc/vim
RUN git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
RUN vim +PluginInstall +qall
RUN cd ~/.vim/bundle/YouCompleteMe && ./install.py --clang-completer
RUN cd ~/.vim/bundle/vim-colorschemes/ && cp -r colors ~/.vim/

# install less for better git log/diff displays
RUN apt-get install -y less

# Install Packages
RUN pip3 install numpy jupyter scipy matplotlib pandas scikit-learn
