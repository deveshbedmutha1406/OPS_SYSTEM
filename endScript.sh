#!/bin/bash
cd "$(dirname "$0")";

testid="$1"

for i in {1..2}; do
  cont_name="container_${testid}_${i}"
  /usr/local/bin/docker kill $cont_name
  /usr/local/bin/docker rm $cont_name
done
dir_name="./containers/${testid}"
rm -r $dir_name
