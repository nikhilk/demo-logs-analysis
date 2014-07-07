#!/bin/sh

export METADATA_HOST=localhost
export METADATA_PORT=8889
export PYTHONPATH=$PWD/modules

ipython notebook --no-mathjax --pylab=inline --port=8888 --ip="127.0.0.1" --notebook-dir=$PWD/notebooks

