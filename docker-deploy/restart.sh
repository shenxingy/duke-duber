docker-compose down --volumes --remove-orphans
docker system prune -a --volumes -f
docker images  # List all images
docker rmi $(docker images -q)  # Remove all images
docker builder prune --all --force
docker-compose up --build