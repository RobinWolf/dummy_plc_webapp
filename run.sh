#!/bin/bash
uid=$(eval "id -u")
gid=$(eval "id -g")


##############################################################################
##                            Run the container                             ##
##############################################################################
SRC_CONTAINER=/home/dummy_plc/src
SRC_HOST="$(pwd)"/src                           

docker run \
  --name dummy_plc \
  --rm \
  -it \
  --net=host \
  -e DISPLAY="$DISPLAY" \
  -v "$SRC_HOST":"$SRC_CONTAINER":rw \
  --gpus 'all,"capabilities=compute,utility,graphics"' \
  --runtime nvidia \
  dummy_plc/flask 