FROM ubuntu:20.04

RUN apt update && apt -y upgrade

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt -y install build-essential
RUN apt -y install swig
RUN apt -y install libsundials-dev
RUN apt -y install libboost-filesystem-dev
RUN apt -y install libboost-date-time-dev
RUN apt -y install libboost-test-dev
RUN apt -y install python3
RUN apt -y install python3-pip

RUN pip3 install \
    dataclasses==0.6 \
    fmipp==2.1.0 \
    mosaik==2.6.1 \
    mosaik-api==2.4.2 \
    numba==0.56.0 \
    networkx==2.5.1 \
    numpy==1.22.4 \
    pandapipes==0.6.0 \
    pandapower==2.8.0 \
    pandas==1.4.3 \
    scipy==1.8.1 \
    simple-pid==1.0.1 \
    simpy==3.0.13 \
    simpy.io==0.2.3 \
    tables==3.7.0 \
    matplotlib

RUN pip3 install --no-cache-dir \
    notebook \
    jupyterlab \
    jupyterhub

ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

WORKDIR ${HOME}
