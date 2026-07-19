# 🎬 Movie Recommendation System

A production-ready Movie Recommendation System built using **FastAPI**, **FAISS**, **Redis**, **Docker**, and **Prometheus/Grafana**. The project demonstrates how to build, optimize, monitor, and test a recommendation service similar to those used in real-world streaming platforms.

---

# Features

* Personalized movie recommendations based on user watch history
* Semantic similarity search using FAISS
* Redis caching for user embeddings and recommendations
* REST API built with FastAPI
* Health check endpoints
* Prometheus metrics for monitoring
* Grafana dashboards for visualization
* Dockerized application
* Automated testing with pytest
* Mock-based unit tests
* Structured logging

---

# Tech Stack

| Category         | Technology             |
| ---------------- | ---------------------- |
| Backend          | FastAPI                |
| Language         | Python                 |
| Vector Search    | FAISS                  |
| Cache            | Redis                  |
| Containerization | Docker, Docker Compose |
| Monitoring       | Prometheus, Grafana    |
| Testing          | Pytest, unittest.mock  |
| Data Processing  | Pandas, NumPy          |

---

# Project Structure

```text
movie-recommender/
│
├── app.py
├── recommend.py
├── redis_client.py
├── metrics.py
├── metrics_router.py
├── health.py
├── logger.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── prometheus.yml
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_recommend.py
│   └── test_recommend_mock.py
│
├── movies.csv
├── user_history.csv
├── movie_embeddings.npy
└── movie_index.faiss
```

---

# System Architecture

```text
                Client
                  │
                  ▼
             FastAPI API
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
     Redis Cache        Recommendation Engine
                              │
                              ▼
                           FAISS Index
                              │
                              ▼
                      Movie Embeddings
```

---

# API Endpoints

| Method | Endpoint                    | Description                    |
| ------ | --------------------------- | ------------------------------ |
| GET    | `/recommend/user/{user_id}` | Get recommendations for a user |
| GET    | `/health`                   | Application health             |
| GET    | `/health/redis`             | Redis connectivity             |
| GET    | `/health/faiss`             | FAISS index status             |
| GET    | `/metrics`                  | Prometheus metrics             |

---

# Running the Project

## Clone the repository

```bash
git clone <repository-url>
cd movie-recommender
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run locally

```bash
uvicorn app:app --reload
```

---

# Running with Docker

Build and start all services:

```bash
docker compose up --build
```

Stop services:

```bash
docker compose down
```

---

# Monitoring

The project includes production monitoring using Prometheus and Grafana.

### Prometheus

```
http://localhost:9090
```

### Grafana

```
http://localhost:3000
```

---

# Metrics Collected

* Total API requests
* API latency
* FAISS searches
* Redis cache hits
* Redis cache misses
* Recommendation cache hits
* Recommendation cache misses

---

# Testing

Run the full test suite:

```bash
python -m pytest
```

Run tests with coverage:

```bash
python -m pytest --cov=. --cov-report=term-missing
```

---

# Sample Response

```json
{
  "recommendations": [
    {
      "movieId": 175,
      "title": "Kids (1995)"
    },
    {
      "movieId": 296,
      "title": "Pulp Fiction (1994)"
    }
  ]
}
```


---

# Learning Outcomes

This project demonstrates practical experience with:

* REST API development using FastAPI
* Recommendation system design
* Vector similarity search using FAISS
* Redis caching strategies
* Docker and containerization
* Health checks and observability
* Prometheus and Grafana monitoring
* Automated testing with pytest
* Mocking and unit testing
* Production-oriented backend development

---

# License

This project is intended for learning, experimentation, and portfolio purposes.