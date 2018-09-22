## All-in-one Docker image for Deep Learning
Here are Dockerfiles to get you up and running with a fully functional deep learning machine. It contains all the popular deep learning frameworks with GPU support (CUDA and cuDNN included).

If you are not familiar with Docker, but would still like an all-in-one solution, start here: [What is Docker?](#what-is-docker). If you know what Docker is, but are wondering why we need one for deep learning, [see this](#why-do-i-need-a-docker)

## Specs
This is what you get out of the box when you create a container with the provided image/Dockerfile:
* Ubuntu 16.04
* [CUDA 9.0](https://developer.nvidia.com/cuda-toolkit) (GPU version only)
* [cuDNN v7](https://developer.nvidia.com/cudnn) (GPU version only)
* [Tensorflow v1.11.0-rc1](https://www.tensorflow.org/)
* [NVIDIA Caffe v0.17](https://github.com/NVIDIA/nvidia-docker/wiki/NVIDIA-Caffe)
* [PyTorch v0.4.1](http://pytorch.org/)
* [Caffe2](https://caffe2.ai/)
* [iPython/Jupyter Notebook](http://jupyter.org/) (including iTorch kernel)
* [Numpy](http://www.numpy.org/), [SciPy](https://www.scipy.org/), [Pandas](http://pandas.pydata.org/), [Scikit Learn](http://scikit-learn.org/), [Matplotlib](http://matplotlib.org/)
* A few common libraries used for deep learning

## Setup
### Prerequisites
1. Install Docker following the installation guide for your platform: [https://docs.docker.com/engine/installation/](https://docs.docker.com/engine/installation/)

2. Install Nvidia drivers on your machine either from [Nvidia](http://www.nvidia.com/Download/index.aspx?lang=en-us) directly or follow the instructions [here](https://github.com/saiprashanths/dl-setup#nvidia-drivers). Note that you _don't_ have to install CUDA or cuDNN. These are included in the Docker container.

3. Install nvidia-docker: [https://github.com/NVIDIA/nvidia-docker](https://github.com/NVIDIA/nvidia-docker), following the instructions [here](https://github.com/NVIDIA/nvidia-docker/wiki/Installation). This will install a replacement for the docker CLI. It takes care of setting up the Nvidia host driver environment inside the Docker containers and a few other things.

### Build the Docker image locally
Alternatively, you can build the images locally. Also, since the GPU version is not available in Docker Hub at the moment, you'll have to follow this if you want to GPU version. Note that this will take an hour or two depending on your machine since it compiles a few libraries from scratch.

```bash
git clone https://github.com/kertansul/dl-docker.git
cd dl-docker
```	

**Python3 Version**
```bash
cd tf-caffe-pytorch
nvidia-docker build -t kertansul/dl-docker:py3 -f Dockerfile.py3 .
```

**Python2 Version**
```bash
cd tf-caffe-pytorch
nvidia-docker build -t kertansul/dl-docker:py2 -f Dockerfile.py2 .
```
This will build a Docker image named `dl-docker` and tagged `pyX` depending on the tag your specify.

## Running the Docker image as a Container
Once we've built the image, we have all the frameworks we need installed in it. We can now spin up one or more containers using this image, and you should be ready to [go deeper](http://imgur.com/gallery/BvuWRxq)
	
**Python3 Version**
```bash
nvidia-docker run -it -p 8888:8888 -p 6006:6006 -v /sharedfolder:/root/sharedfolder kertansul/dl-docker:py3 bash
```
Note the use of `nvidia-docker` rather than just `docker`

| Parameter      | Explanation |
|----------------|-------------|
|`-it`             | This creates an interactive terminal you can use to iteract with your container |
|`-p 8888:8888 -p 6006:6006`    | This exposes the ports inside the container so they can be accessed from the host. The format is `-p <host-port>:<container-port>`. The default iPython Notebook runs on port 8888 and Tensorboard on 6006 |
|`-v /sharedfolder:/root/sharedfolder/` | This shares the folder `/sharedfolder` on your host machine to `/root/sharedfolder/` inside your container. Any data written to this folder by the container will be persistent. You can modify this to anything of the format `-v /local/shared/folder:/shared/folder/in/container/`. See [Docker container persistence](#docker-container-persistence)
|`kertansul/dl-docker:py3`   | This the image that you want to run. The format is `image:tag`. In our case, we use the image `dl-docker` and tag `py3` |
|`bash`       | This provides the default command when the container is started. Even if this was not provided, bash is the default command and just starts a Bash session. You can modify this to be whatever you'd like to be executed when your container starts. For example, you can execute `docker run -it -p 8888:8888 -p 6006:6006 kertansul/dl-docker:py3 jupyter notebook`. This will execute the command `jupyter notebook` and starts your Jupyter Notebook for you when the container starts


To utilize other GPUs, use the pre-defined script function `set_gpu`.
For example, if you want to utilize GPU0 and GPU3, issue
```
set_gpu 0,3
```

## Some common scenarios
### Jupyter Notebooks
The container comes pre-installed with iPython and iTorch Notebooks, and you can use these to work with the deep learning frameworks. If you spin up the docker container with `docker-run -p <host-port>:<container-port>` (as shown above in the [instructions](#running-the-docker-image-as-a-container)), you will have access to these ports on your host and can access them at `http://127.0.0.1:<host-port>`. The default iPython notebook uses port 8888 and Tensorboard uses port 6006. Since we expose both these ports when we run the container, we can access them both from the localhost.

However, you still need to start the Notebook inside the container to be able to access it from the host. You can either do this from the container terminal by executing `jupyter notebook --allow-root` or you can pass this command in directly while spinning up your container using the `docker run -it -p 8888:8888 -p 6006:6006 kertansul/dl-docker:py3 jupyter notebook --allow-root` CLI. The Jupyter Notebook has both Python (for TensorFlow, Caffe, Theano, Keras, Lasagne) and iTorch (for Torch) kernels.

### Data Sharing
See [Docker container persistence](#docker-container-persistence). 
Consider this: You have a script that you've written on your host machine. You want to run this in the container and get the output data (say, a trained model) back into your host. The way to do this is using a [Shared Volumne](#docker-container-persistence). By passing in the `-v /sharedfolder/:/root/sharedfolder` to the CLI, we are sharing the folder between the host and the container, with persistence. You could copy your script into `/sharedfolder` folder on the host, execute your script from inside the container (located at `/root/sharedfolder`) and write the results data back to the same folder. This data will be accessible even after you kill the container.

## What is Docker?
[Docker](https://www.docker.com/what-docker) itself has a great answer to this question.

Docker is based on the idea that one can package code along with its dependencies into a self-contained unit. In this case, we start with a base Ubuntu 16.04 image, a bare minimum OS. When we build our initial Docker image using `docker build`, we install all the deep learning frameworks and its dependencies on the base, as defined by the `Dockerfile`. This gives us an image which has all the packages we need installed in it. We can now spin up as many instances of this image as we like, using the `docker run` command. Each instance is called a _container_. Each of these containers can be thought of as a fully functional and isolated OS with all the deep learning libraries installed in it. 

## Why do I need a Docker?
Installing all the deep learning frameworks to coexist and function correctly is an exercise in dependency hell. Unfortunately, given the current state of DL development and research, it is almost impossible to rely on just one framework. This Docker is intended to provide a solution for this use case.

If you would rather install all the frameworks yourself manually, take a look at this guide: [Setting up a deep learning machine from scratch](https://github.com/saiprashanths/dl-setup)

 
### How do I update/install new libraries?
You can do one of:

1. Modify the `Dockerfile` directly to install new or update your existing libraries. You will need to do a `docker build` after you do this. If you just want to update to a newer version of the DL framework(s), you can pass them as CLI parameter using the --build-arg tag ([see](-v /sharedfolder:/root/sharedfolder) for details). The framework versions are defined at the top of the `Dockerfile`. For example, `docker build -t kertansul/dl-docker:py3 -f Dockerfile.py3 --build-arg TF_BRANCH=r1.3 .`

2. You can log in to a container and install the frameworks interactively using the terminal. After you've made sure everything looks good, you can commit the new contains and store it as an image
