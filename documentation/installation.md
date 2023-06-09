# Installation

# Conda environments

prefix given in the `py_test.yml`

To install locally put your location when running command
**Do not forget to change the location of installation (prefix in py_test.yml)**

```bash
conda env create --file py_test.yml
```

# Docker build from file

```bash
docker build --no-cache --progress=plain --file py_test_dockerfile --tag py_test:latest .  2>&1 | tee build.logs

docker images
# to remove
# docker rmi <img id>
# Testing
docker run -it py_test bash

# push to docker hub
docker login
docker tag py_test evezeyl/py_test
docker push evezeyl/py_test
```
