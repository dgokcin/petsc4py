### To solve the test matrix

```sh
docker run -it denizgokcin/petsc4py:latest /bin/bash
python3 MatrixSolver.py
```

### To run with specific number of CPUs

```sh
docker run -it --cpus <CPU_COUNT> denizgokcin/petsc4py:latest /bin/bash
python3 MatrixSolver.py
```

### To run a custom python script inside the current directory
- Make sure that you enabled file sharing between the docker host and the images

```sh
docker run -it -v ${pwd}/customScript.py:/app/customScript.py --cpus <CPU_COUNT> denizgokcin/petsc4py:latest /bin/bash
python3 customScript.py
```

### To build PETSc image

```sh
docker build -t petsc4py -f petsc.dockerfile .
```

### To extend the docker image

```dockerfile
FROM denizgokcin/petsc4py:0.0.1

RUN apt-get update \
  && apt-get install -y \
    curl \
    vim

RUN pip3 install \
    h5py \
    pandas
```
