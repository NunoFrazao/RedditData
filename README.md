# ISAWS-Project
Intelligent Sentiment Analysys Web System (ISAWS)

# Node Build (before docker build)
fazer o build sem o npm instalado na maquina

docker run -v ./PLN:/app -w /app -it node:20.16-slim npm run install
docker run -v ./PLN:/app -w /app -it node:20.16-slim npm run build


# Docker build
docker compose -f docker-compose.build.yml up -d --build

tag <imagem-laravel> isaws-laravel:latest
tag <imagem-search-engine> isaws-search-engine:latest

docker compose up -d --build

# Docker run

docker compose up -d