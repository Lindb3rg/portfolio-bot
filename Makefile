.PHONY: build compose up down logs restart clean forcebuild

# Build the Docker image
build:
	docker build -t portfolio-bot .

forcebuild:
	docker build --no-cache -t portfolio-bot .

# Run with docker-compose
compose:
	docker compose up

# Alternative to run in detached mode
up:
	docker compose up -d

# Stop containers
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Restart containers
restart:
	docker-compose restart

# Clean up dangling images and stopped containers
clean:
	docker system prune -f

# Build and run in one command
all: build compose