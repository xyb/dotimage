DotImage
========

Convert profiling output to a dot graph using [Gprof2Dot](https://code.google.com/p/jrfonseca/wiki/Gprof2Dot).

run
---

    ./dotimage.py

docker
------

[DotImage in docker](https://registry.hub.docker.com/u/xieyanbo/dotimage/):

    docker run -d -p 5000:5000 --name dotimage xieyanbo/dotimage

Or using your own data directory out of the docker box:

    docker run -d -p 5000:5000 --name dotimage \
               -e UPLOAD_FOLDER=/opt -v /tmp/dotimage:/opt xieyanbo/dotimage

and using a browser to access http://your.host.ip:5000/
