##############################################################################################
###                                     Base Image                                         ###
##############################################################################################

FROM docker.io/arm64v8/ubuntu:22.04 AS base

ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES all


# Create user
ARG UID=1000
ARG GID=1000
ARG USER=dummy_plc
ENV USER=$USER
RUN groupadd -g $GID $USER \
    && useradd -m -u $UID -g $GID --shell $(which bash) $USER
RUN usermod -aG sudo,video "$USER"


##############################################################################################
###                           dummy plc installations (flask)                              ###
##############################################################################################
FROM base AS flask_framework

# Setup workpace
USER $USER
RUN mkdir -p /home/$USER/src
WORKDIR /home/$USER/src/plc_webapp

# Install flask
USER root
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install flask
RUN pip install flask-socketio
USER $USER

# Run the webapp
CMD ["python3", "app.py"]