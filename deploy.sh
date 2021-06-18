docker build -t wtr-mngr/cv-server .
docker stop cv-server
docker rm cv-server
docker run -d -p 5000:5000 --name cv-server wtr-mngr/cv-server