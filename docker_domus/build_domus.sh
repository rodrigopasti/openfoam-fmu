#!/bin/bash

version=0.00
dev=true # true or false
upload_cloud=true # true or false
latest=true  # true or false
build=full   #full or core


image_name=domus
docker_img=ubuntu:22.04
openfoam_img=${image_name}:${version}
base_name=rodrigopasti/domus-base


if [ "$build" = "full" ]; then
  docker build --no-cache -t $base_name --build-arg img=$docker_img --build-arg private_key="$pk_bq" -f base.dockerfile .
fi

  #docker build --no-cache -t domus-base --build-arg img=ubuntu:22.04 --build-arg private_key="$pk_bq" -f base.dockerfile
  #docker build --no-cache -t ${base_name} --build-arg img=$base_name -f foam.dockerfile .

  #if [ "$upload_cloud" = "true" ]; then
  #  docker tag axon/${openfoam_img} sa-saopaulo-1.ocir.io/grr1zbdsa9ua/${openfoam_img}
  #  docker push sa-saopaulo-1.ocir.io/grr1zbdsa9ua/${openfoam_img}
  #fi

  #if [ "$latest" = "true" ]; then
  #  docker tag axon/${openfoam_img} axon/${image_name}:latest
  #fi

