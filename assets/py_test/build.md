Building checkr container for DPI

```shell
# if docker error network https://stackoverflow.com/questions/39508018/docker-driver-failed-programming-external-connectivity-on-endpoint-webserver
service docker restart
# building
docker buildx build -f Dockerfile  -t "py_test:latest" .

# tagging and push 
docker tag py_test evezeyl/py_test
docker push evezeyl/py_test


