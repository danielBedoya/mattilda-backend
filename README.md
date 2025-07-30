# Mattilda Backend

This repository contains the backend services for the Mattilda application.

## Table of Contents

- [Local Development Setup](#local-development-setup)
  - [Prerequisites](#prerequisites)
  - [Running the Application](#running-the-application)
- [Deployment](#deployment)
  - [Prerequisites](#deployment-prerequisites)
  - [Building Docker Images](#building-docker-images)
  - [Running with Docker Compose](#running-with-docker-compose)
  - [Database Migrations](#database-migrations)
- [Environment Variables](#environment-variables)

## Local Development Setup

### Prerequisites

Before you begin, ensure you have the following installed:

- Docker and Docker Compose

### Running the Application

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/mattilda-backend.git
    cd mattilda-backend
    ```

2.  **Set up environment variables:**

    Create a `.env` file in the root directory based on `.env.example` (if available) or the [Environment Variables](#environment-variables) section.

3.  **Run the application with Docker Compose:**

    ```bash
    docker-compose up
    ```

    This command will build the necessary Docker images and start all the services, including the FastAPI application, PostgreSQL, and Redis. The API will be available at `http://localhost:8000`.

## Deployment

This section outlines the steps to deploy the Mattilda backend using Docker.

### Deployment Prerequisites

- A server with Docker and Docker Compose installed.
- Appropriate environment variables configured for your production environment.

### Building Docker Images

Navigate to the project root and build your Docker images:

```bash
docker-compose build
```

### Running with Docker Compose

To start all services defined in `docker-compose.yml`:

```bash
docker-compose up -d
```

This will start the FastAPI application, PostgreSQL, and Redis in detached mode.

### Database Migrations

After deploying, you need to run database migrations to ensure your database schema is up-to-date. This can be done by executing the `alembic upgrade head` command within the application container. You might need to exec into the running application container:

```bash
docker-compose exec <app-service-name> alembic upgrade head
```

Replace `<app-service-name>` with the actual service name of your FastAPI application in `docker-compose.yml` (e.g., `web` or `api`).

## Environment Variables

The application relies on several environment variables for configuration. These should be set in your deployment environment (e.g., via a `.env` file, Docker Compose environment section, or your CI/CD pipeline).

Here are some common variables you might need to configure:

- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:password@host:port/dbname`)
- `REDIS_HOST`: Redis host (e.g., `localhost`)
- `REDIS_PORT`: Redis port (e.g., `6379`)
- `SECRET_KEY`: A strong secret key for security purposes (e.g., for JWTs)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time for access tokens
- `DEBUG`: Set to `False` in production

**Note:** This list is illustrative. Refer to the application's source code (e.g., `app/core/config.py` if it exists) for the exact required environment variables.