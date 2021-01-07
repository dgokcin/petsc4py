ARG alpine_version=3.12
FROM "alpine:${alpine_version}"

################################################################################
# Modifiable (e.g. via command line) args.                                     #
################################################################################

ARG build_processors=1
ARG USER=petsc4py
ARG PETSC_VERSION=3.14.2
ARG MPICH_VERSION=3.2
ARG MPI4PY_VERSION=3.0.3
ARG NUMPY_VERSION=1.19.4
ARG PANDAS_VERSION=1.2.0

################################################################################
# Local vars (not for modification!)                                           #
################################################################################

ARG home_dir=/home/${USER}
ARG dir_build="${home_dir}/build"
ARG dir_downloads="${home_dir}/downloads"
ARG petsc_dir="${home_dir}/petsc"

# Set up permissions for non-root usage
USER root
# Note need to set up /usr/bin/python symlink to point to python3
ARG REQUIRE="sudo build-base wget bash \
             ca-certificates git gcc gfortran\
             python3 python3-dev py3-scipy\
             py3-pip cython cmake g++ libxslt-dev\
             patch make bison flex"

RUN apk update && apk upgrade \
      && apk add --no-cache ${REQUIRE} \
      && rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python

# Commenting out to make everything run as root for now
#RUN addgroup -g 10101 ${USER} && \
    #adduser -D -u 10101 -s /bin/bash -h /home/${USER} -G ${USER} ${USER}

ENV PATH=${petsc_dir}/bin:${PATH}

#USER ${USER}

RUN mkdir -p ${dir_downloads} ${petsc_dir} ${dir_build}

#------------------------------------------------------------------------------#
# Download dependencies
#------------------------------------------------------------------------------#

RUN cd ${dir_downloads} && \
    wget https://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-lite-${PETSC_VERSION}.tar.gz && \
    wget https://www.mpich.org/static/downloads/${MPICH_VERSION}/mpich-${MPICH_VERSION}.tar.gz
 

RUN pip3 install --no-cache-dir numpy==${NUMPY_VERSION} pandas==${PANDAS_VERSION}
    
#------------------------------------------------------------------------------#
# Build petsc
#------------------------------------------------------------------------------#

RUN cd ${dir_build} && \
    tar -zxf ${dir_downloads}/petsc-lite-${PETSC_VERSION}.tar.gz && \
    cd petsc-${PETSC_VERSION} && \
    export PETSC_DIR=`pwd` && \
    export PETSC_ARCH=linux-gnu-opt && \
    ./configure --prefix=${petsc_dir} \
                --with-make-np=${build_processors} \
                --with-cc=gcc \
                --with-cxx=g++ \
                --with-fc=gfortran \
                --with-x=false \
                --with-ssl=false \
                --download-mpi4py=yes\
                --with-mpi4py=yes\
                --download-petsc4py=yes\
                --with-petsc4py=yes\
                --download-mumps\
                --download-scalapack\
                --download-parmetis\
                --download-metis\
                --download-ptscotch\
                --download-f2cblaslapack=1 \
                --download-mpich=${dir_downloads}/mpich-${MPICH_VERSION}.tar.gz \
                --with-shared-libraries \
                --with-debugging=0 && \
    make all test && \
    make install

# Add ${petsc_dir}/lib to PYTHONPATH for proper usage of mpi4py.
ENV PYTHONPATH=${petsc_dir}/lib\
    PETSC_DIR=${petsc_dir}

# Clean up downloads
RUN rm -rf ${dir_downloads}

# Copy the python script
RUN mkdir -p ${home_dir}/app
WORKDIR /matrices

#COPY ./solver/ .
CMD ["bash"]
