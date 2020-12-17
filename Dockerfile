FROM ubuntu:20.04

ENV TZ=Europe/Istanbul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# Install the dependencies
RUN apt-get update \
  && apt-get install -y \
    git \
    wget \
    make \
    gcc \
    gfortran \
    mpich \
    zlib1g \
    python3 \
    python3-pip \
    pkg-config


ENV SWDIR=/opt

WORKDIR ${SWDIR}

# Clone the petsc repository
RUN git clone https://gitlab.com/petsc/petsc.git

# Install python dependencies needed for petsc
RUN pip3 install cython numpy

# Configure and build PETSc
WORKDIR ${SWDIR}/petsc
RUN printf "\n=== Configuring PETSc without batch mode & installing\n"
RUN ./configure --with-cc=gcc\
    --with-cxx=g++\
    --download-fblaslapack\
    --with-fortran-bindings=0\
    --download-mpich\
    --download-petsc4py=yes\
    --download-mpi4py=yes\
    --with-mpi4py=yes\
    --with-petsc4py=yes&& \
    make all && \
    make test

# Install python dependencies needed for the MatrixSolver app
RUN pip3 install mpi4py scipy

ENV PETSC_DIR=${SWDIR}/petsc

# Manually build and setup petsc4py
WORKDIR ${SWDIR}/petsc/src/binding/petsc4py
RUN python3 setup.py build && python3 setup.py install

# Copy the python script
WORKDIR /app
COPY ./MatrixSolver.py .

#ENTRYPOINT ["python3", "MatrixSolver.py"]
