ARG alpine_version=3.12
FROM "alpine:${alpine_version}"

################################################################################
# Modifiable (e.g. via command line) args.                                     #
################################################################################

ARG build_processors=1
ARG USER=petsc4py
ARG PETSC_VERSION=3.12.4
ARG MPICH_VERSION=3.2
ARG MPI4PY_VERSION=3.0.3
ARG PETSC4PY_VERSION=3.12.0
ARG MPICH_CONFIGURE_OPTIONS
ARG MPICH_MAKE_OPTIONS

################################################################################
# Local vars (not for modification!)                                           #
################################################################################

ARG home_dir=/home/${USER}
ARG dir_build="${home_dir}/build"
ARG dir_chaste_libs="${home_dir}/chaste-libs"
ARG dir_downloads="${home_dir}/downloads"

################################################################################
# 1. Install "chaste-libs" - ApPredict's dependencies                          #
#                                                                              #
# https://chaste.cs.ox.ac.uk/trac/wiki/InstallGuides/DependencyVersions        #
# https://chaste.cs.ox.ac.uk/trac/wiki/InstallGuides/InstallGuide              #
################################################################################

USER root
# See http://nl.alpinelinux.org/alpine/v3.12/main/x86_64/   <-- Note: v3.12!
# Note need to set up /usr/bin/python symlink to point to python3
ARG REQUIRE="sudo build-base wget bash \
             ca-certificates git gcc gfortran\
             python3 python3-dev py3-scipy\
             py3-numpy cython cmake g++ libxslt-dev\
             patch make"

RUN apk update && apk upgrade \
      && apk add --no-cache ${REQUIRE} \
      && rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python

RUN addgroup -g 10101 ${USER} && \
    adduser -D -u 10101 -s /bin/bash -h /home/${USER} -G ${USER} ${USER}

ENV PATH=${dir_chaste_libs}/bin:${PATH}
ENV LD_LIBRARY_PATH=${dir_chaste_libs}/lib

USER ${USER}

RUN mkdir -p ${dir_downloads} ${dir_chaste_libs} ${dir_build}

#------------------------------------------------------------------------------#
# 1.1. Download dependency packages                                            #
#------------------------------------------------------------------------------#

RUN cd ${dir_downloads} && \
    wget https://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-lite-${PETSC_VERSION}.tar.gz && \
    wget https://www.mpich.org/static/downloads/${MPICH_VERSION}/mpich-${MPICH_VERSION}.tar.gz && \
    wget https://bitbucket.org/mpi4py/mpi4py/downloads/mpi4py-${MPI4PY_VERSION}.tar.gz && \
    wget https://bitbucket.org/petsc/petsc4py/petsc4py-${PETSC4PY_VERSION}.tar.gz
    

#------------------------------------------------------------------------------#
# 1.2. Build dependencies and place in ${dir_chaste_libs}                      #
#------------------------------------------------------------------------------#

RUN cd ${dir_build} && \
    tar -zxf ${dir_downloads}/petsc-lite-${PETSC_VERSION}.tar.gz && \
    cd petsc-${PETSC_VERSION} && \
    export PETSC_DIR=`pwd` && \
    export PETSC_ARCH=linux-gnu-opt && \
    ./configure --prefix=${dir_chaste_libs} \
                --with-make-np=${build_processors} \
                --with-cc=gcc \
                --with-cxx=g++ \
                --with-fc=0 \
                --with-x=false \
                --with-ssl=false \
                --download-f2cblaslapack=1 \
                --download-mpich=${dir_downloads}/mpich-${MPICH_VERSION}.tar.gz \
                --with-shared-libraries \
                --with-debugging=0 && \

    make all test && \
    make install

