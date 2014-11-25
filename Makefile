build:
	docker build -rm -t dotimage .

run:
	docker run -d -p 8001:5000 -e DEBUG=1 --name dotimage dotimage
