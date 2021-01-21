[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/dgokcin/petsc4py/ci?&logo=github-actions)](https://github.com/dgokcin/petsc4py/actions)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/dgokcin/petsc4py?logo=github)](https://github.com/dgokcin/petsc4py/releases)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/denizgokcin/petsc4py?logo=docker&sort=semver)](https://hub.docker.com/repository/docker/denizgokcin/petsc4py/tags?page=1&ordering=last_updated)
[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/denizgokcin/petsc4py?logo=docker&sort=semver)]()
[![Docker Pulls](https://img.shields.io/docker/pulls/denizgokcin/petsc4py?logo=docker)]()

### Description 
A Dockerized environment with petsc and its python dependencies bundled
together.

### Usage
![](https://github.com/dgokcin/petsc4py/blob/master/doc/usage.gif)
### Changelog

| Image Tag | Image Size | Description                                                                                                                 |
|-----------|------------|-----------------------------------------------------------------------------------------------------------------------------|
| v0.0.9    | 843.26MB      |reverted back petsc to petsc-lite                                                                                          |
| v0.0.8    | 891.6MB      |updated the petsc version, switched to petsc instead of petsc-lite, added mumps dependencies                               |
| v0.0.7    | 578.68MB      |added the pandas python package to the container, install python packages with --no-cache-dir option                      |
| v0.0.6    | 547.11MB      |got rid of the petsc4py, using the root user instead since it caused problems in the latest version of the solver.        |
| v0.0.5    | 547.28MB      |changed the base image from debian slim to alpine 3.12, adjusted the permissions so that the image works as non-root user |
| v0.0.4    | 547.27MB      |changed the base image from debian slim to alpine 3.12, adjusted the permissions so that the image works as non-root user |
| v0.0.3    | 1.78GB     |changed the base image from ubuntu 20.04 to debian-slim                                                                      |
| v0.0.2    | 1.77GB     |changed theentrypoint to the container for easier use                                                                        |
| v0.0.1    | 1.77GB     |initial setup, bundled  all the  dependencies of  petsc                                                                      |

### To run the solver with mounted matrices dir

```sh
docker run -it -d -w /matrices -v /matrices:/matrices denizgokcin/petsc4py:v0.0.9 /bin/bash -c './run_for_docker.sh beta.lst'
```

### To run two solvers with mounted matrices dir

```sh
cd <PATH_FOR_THE_MATRICES_DIR>
docker-compose up --scale app=2 -d
```
### To build PETSc image

```sh
docker build -t petsc4py .
```

### To extend the docker image

```dockerfile
FROM denizgokcin/petsc4py:<TAG_NAME>

RUN apt-get update \
  && apt-get install -y \
    curl \
    vim

RUN pip3 install \
    h5py \
    pandas
```
