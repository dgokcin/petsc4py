FROM alpine:latest
# In case the main package repositories are down, use the alternative base image:
# FROM gliderlabs/alpine:3.4

MAINTAINER Nikyle Nguyen <NLKNguyen@MSN.com>

ARG REQUIRE="sudo build-base wget bash ca-certificates git gcc gfortran  python3 py3-pip python3-dev"
RUN apk update && apk upgrade \
      && apk add --no-cache ${REQUIRE}

ENV SWDIR=/opt
ENV MPICH_VERSION=3.2
WORKDIR ${SWDIR}

# Downloa dmpich
RUN wget https://www.mpich.org/static/downloads/${MPICH_VERSION}/mpich-${MPICH_VERSION}.tar.gz

# Clone the petsc repository
RUN git clone https://gitlab.com/petsc/petsc.git

# Install python dependencies needed for petsc
RUN pip3 install cython numpy

# Configure and build PETSc
WORKDIR ${SWDIR}/petsc
RUN printf "\n=== Configuring PETSc without batch mode & installing\n"
RUN ./configure \
    --with-cc=gcc\
    --with-cxx=g++\
    --with-fc=0\
    --download-mpich=${SWDIR}/mpich-${MPICH_VERSION}.tar.gz \
    --download-f2cblaslapack=1 \
    --download-petsc4py=yes\
    --download-mpi4py=yes\
    --with-mpi4py=yes\
    --with-petsc4py=yes&& \
    make all && \
    make test

# Install python dependencies needed for the MatrixSolver app
RUN apk add py3-scipy

ENV PETSC_DIR=${SWDIR}/petsc

# Manually build and setup petsc4py
WORKDIR ${SWDIR}/petsc/src/binding/petsc4py
RUN python3 setup.py build && python3 setup.py install

# Manually build and setup mpi4py
WORKDIR ${SWDIR}/petsc/arch-linux-c-debug/externalpackages/mpi4py-3.0.3
RUN python3 setup.py build && python3 setup.py install

# Download, build, and install MPICH
RUN mkdir /tmp/mpich-src
WORKDIR /tmp/mpich-src
RUN wget http://www.mpich.org/static/downloads/${MPICH_VERSION}/mpich-${MPICH_VERSION}.tar.gz \
      && tar xfz mpich-${MPICH_VERSION}.tar.gz  \
      && cd mpich-${MPICH_VERSION}  \
      && ./configure ${MPICH_CONFIGURE_OPTIONS}  \
      && make ${MPICH_MAKE_OPTIONS} && make install \
      && rm -rf /tmp/mpich-src


# Copy the python script
WORKDIR /app
COPY ./MatrixSolver.py .

CMD ["python3", "MatrixSolver.py"]
