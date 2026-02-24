# Backend (`backend/`)

This folder contains the backend app for the crewboard project. The backend comes with its own separate tests.

## Docker

The backend is shipped with its own container. This can run independetly or can be easily started together with the database by running the docker compose yaml.

### Build

```bash
docker build -t crewboard-backend -f backend/.Dockerfile .
```

### Run

```bash
docker run -p 8001:8001 --env-file backend/.env crewboard-backend
```

