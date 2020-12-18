[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/dgokcin/petsc4py/ci?&logo=github-actions)](https://github.com/dgokcin/petsc4py/actions)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/dgokcin/petsc4py?logo=github)](https://github.com/dgokcin/petsc4py/releases)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/denizgokcin/petsc4py?logo=docker&sort=semver)](https://hub.docker.com/repository/docker/denizgokcin/petsc4py/tags?page=1&ordering=last_updated)
[![Docker Image Size (latest semver)](https://img.shields.io/docker/image-size/denizgokcin/petsc4py?logo=docker&sort=semver)]()
[![Docker Pulls](https://img.shields.io/docker/pulls/denizgokcin/petsc4py?logo=docker)]()

### Description 
A Dockerized environment with petsc and its python dependencies bundled together.

### To solve the test matrix

```sh
docker run -it --rm denizgokcin/petsc4py:latest
```

### To solve the test matrix with specific number of CPUs

```sh
docker run -it --rm --cpus <CPU_COUNT> denizgokcin/petsc4py:latest
```

### To run a custom python script inside the current directory
- Make sure that you enabled file sharing between the docker host and the images

```sh
docker run -it --rm -v ${pwd}/customScript.py:/app/customScript.py --cpus <CPU_COUNT> denizgokcin/petsc4py:latest bash
python3 customScript.py
```

### To build PETSc image

```sh
docker build -t petsc4py .
```

### To extend the docker image

```dockerfile
FROM denizgokcin/petsc4py:latest

RUN apt-get update \
  && apt-get install -y \
    curl \
    vim

RUN pip3 install \
    h5py \
    pandas
```

### Changelog

| Image Tag | Description                                             |
|-----------|---------------------------------------------------------|
| v0.0.2    | changed theentrypoint to the container for easier use   |
| v0.0.1    | initial setup, bundled  all the  dependencies of  petsc |
