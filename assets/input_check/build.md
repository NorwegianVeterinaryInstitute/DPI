Building checkr container for DPI

```shell
# if docker error network https://stackoverflow.com/questions/39508018/docker-driver-failed-programming-external-connectivity-on-endpoint-webserver
service docker restart
# building
docker buildx build -f Dockerfile  -t "checkr:latest" .
# checking 
 docker run -it --mount type=bind,source="$(pwd)",target=/app checkr bash 
 Rscript input_check.R --input input_pairs_20SNPs.csv --version TRUE
# tagging and push 
docker tag checkr evezeyl/checkr
docker push evezeyl/checkr



```
singularity pull checkr.sif docker://evezeyl/checkr
singularity shell checkr.sif -bind .
```
