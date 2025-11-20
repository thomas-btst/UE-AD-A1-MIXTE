# UE-AD-A1-MIXTE

This project implements a microservices-based system composed of four independent services: movies, users, schedules, and bookings.
The goal is to demonstrate a heterogeneous architecture using multiple communication protocols (REST, GraphQL, gRPC), fully containerized with Docker.
Services can use either MongoDB or a local JSON file as database.

---

## Architecture

The application is split into four distinct services:

### Movie Service (GraphQL + Flask)

Provides movie and actor information through a GraphQL API.
Data is stored locally in JSON files.

### Booking Service (GraphQL + Flask)

Manages booking operations.
Uses a GraphQL API and communicates with the Schedule service via gRPC.

### User Service (REST + Flask)

Classic REST API managing user data.
Documentation is provided through OpenAPI files in both English and French.
Documentation is available on http://localhost:3004/docs/

### Schedule Service (gRPC)

Provides available movie schedules through a gRPC interface.
The schedule data is stored in a JSON file.

Each service is fully isolated, has its own codebase and Dockerfile, and can be built or run independently.

---

## Structure

```
.
├── movie/             # GraphQL service for movies and actors, includes gRPC client
├── booking/           # GraphQL service for bookings, includes gRPC client
├── user/              # REST service for user management + OpenAPI specs
├── schedule/          # gRPC service providing schedule information
├── insomnia.yml       # Insomnia collection for API testing
├── docker-compose.yml # Orchestrates microservices
├── .env               # Environment variables
└── requirements.txt   # Python dependencies
```

Each service contains:

- a Python application (`*.py`)
- configuration and schema files (`*.graphql`, `*.proto`, OpenAPI YAML…)
- a `data/` folder with its local JSON data
- a `db/` folder which contains the JSON and MongoDB Database implementation
- a `Dockerfile` for building the service container

---

## Deployment with Docker

### Requirements

You must have:

- Docker installed
- Docker Compose installed

### Build all images

```
docker compose build
```

### Start all services

```
docker compose up -d
```

### Stop all services

```
docker compose down
```

---

## Environment Configuration

Each service can use **either MongoDB or a local JSON file** as its database.

A `.env` file is provided at the root of the project.
Inside it, you must define the following variable:

```
DB_TYPE=mongo
```

or

```
DB_TYPE=json
```

---

## Typical Endpoints

| Service  | Protocol | Port | Description                  |
| -------- | -------- | ---- | ---------------------------- |
| Movie    | GraphQL  | 3001 | Movie and actor queries      |
| Schedule | gRPC     | 3002 | Schedule information service |
| Booking  | GraphQL  | 3003 | Booking operations           |
| User     | REST     | 3004 | User management              |

---

## Authors

Project created by:

- **Thomas BATISTA**
- **Youmna ABBOUBI**

This project was developed **as part of our academic studies** and **is not intended for commercial use**.
