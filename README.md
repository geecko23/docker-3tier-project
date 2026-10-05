# Docker 3-Tier Application — Kubernetes + Jenkins CI/CD

A 3-tier Flask application deployed on Kubernetes and automated with a Jenkins CI/CD pipeline.

This project extends the original Dockerized 3-tier application by introducing Kubernetes-based deployment, automated testing, Docker image versioning, Docker Hub publishing, change detection, rolling updates, and Git release tags.

---

## Architecture

```text
                         GitHub
                            │
                            │ Push
                            ▼
                       ┌─────────┐
                       │ Jenkins │
                       └────┬────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
             Test      Build & Push    Git Tag
              │             │             │
              └─────────────┼─────────────┘
                            │
                            ▼
                       Docker Hub
                            │
                            │ Pull image
                            ▼
                      ┌───────────┐
                      │ Kubernetes│
                      │  Minikube │
                      └─────┬─────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
              Nginx        Flask       Redis
                │           │
                │           └───────┐
                │                   │
                │                 MySQL
                │
              User
```

### Application tiers

* **Nginx** — reverse proxy / frontend entry point
* **Flask** — application layer
* **MySQL** — persistent relational database
* **Redis** — visit counter/cache layer

---

## Technologies

* Docker
* Docker Compose
* Kubernetes
* Minikube
* Jenkins
* Git & GitHub
* Docker Hub
* Python
* Flask
* MySQL
* Redis
* Nginx
* pytest

---

## Project Structure

```text
docker-3tier-project/
├── app/
│   ├── app.py
│   ├── requirements.txt
│   ├── test_app.py
│   └── Dockerfile
│
├── db/
│   └── init.sql
│
├── nginx/
│   ├── nginx.conf
│   └── Dockerfile
│
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ...
│
├── compose.yml
├── Jenkinsfile
└── README.md
```

---

# CI/CD Pipeline

The Jenkins pipeline consists of the following stages:

```text
GitHub Push
     │
     ▼
   Test
     │
     ▼
Check App Changes
     │
     ├── No app changes ──► Stop
     │
     ▼
Determine Version
     │
     ▼
Build Docker Image
     │
     ▼
Push to Docker Hub
     │
     ▼
Update Kubernetes
     │
     ▼
Wait for Rollout
     │
     ▼
Create Git Tag
```

## 1. Test

Jenkins creates a Python virtual environment if necessary and installs the application's dependencies.

It then runs:

```bash
pytest
```

The deployment process only continues if the tests pass.

---

## 2. Check App Changes

The pipeline checks whether files inside the `app/` directory changed between the previous successful build and the current commit.

It uses:

```bash
git diff --quiet <previous-commit> <current-commit> -- app/
```

If the application code did not change, the Docker build, Docker Hub push, Kubernetes update, and release tagging stages are skipped.

This prevents unnecessary application deployments when changes only affect other parts of the repository.

---

## 3. Determine Version

Application releases are versioned using Git tags:

```text
v1
v2
v3
...
```

Jenkins finds the latest version using:

```bash
git tag --list 'v*' --sort=-v:refname | head -n 1
```

The next version is then generated automatically.

For example:

```text
Latest tag:       v2
Next application: v3
```

The `v:refname` sorting uses version-aware sorting so that `v10` is correctly considered newer than `v9`.

---

## 4. Build Docker Image

When application code changes, Jenkins builds a new Flask application image.

Example:

```bash
docker build \
    -t docker-3tier-app:jenkins-v3 \
    ./app
```

Only the application image is rebuilt.

The MySQL image is not rebuilt on every application change because the database is stateful and uses persistent storage.

---

## 5. Push to Docker Hub

Jenkins authenticates to Docker Hub using stored Jenkins credentials and pushes the versioned image.

Example:

```text
abrar15/docker-3tier-app:jenkins-v3
```

Versioned images make it possible to identify which application version is deployed.

---

## 6. Update Kubernetes

Jenkins updates the running Kubernetes Deployment using:

```bash
kubectl set image deployment/app \
    app=abrar15/docker-3tier-app:jenkins-v3
```

It then waits for Kubernetes to complete the rollout:

```bash
kubectl rollout status deployment/app
```

This allows the pipeline to detect whether the new application version successfully rolled out.

---

## 7. Create Git Release Tag

The Git tag is created **only after the Kubernetes rollout succeeds**.

For example:

```bash
git tag v3
git push origin v3
```

This makes the Git tag represent a successfully deployed application release.

If the Kubernetes deployment fails, the release tag is not created.

---

# Versioning Strategy

The project uses Git tags and Docker image tags together.

For example:

```text
Git tag:
v3

Docker image:
abrar15/docker-3tier-app:jenkins-v3
```

This provides a simple relationship between the source-code release and the deployed container image.

The versioning flow is:

```text
Application change
       │
       ▼
Determine next version
       │
       ▼
Build jenkins-v3
       │
       ▼
Push jenkins-v3
       │
       ▼
Deploy to Kubernetes
       │
       ▼
Rollout succeeds
       │
       ▼
Create Git tag v3
```

---

# Kubernetes Deployment

The application runs on a local Minikube Kubernetes cluster.

The cluster contains:

```text
Nginx
  │
  ▼
Flask Application
  │
  ├── Redis
  │
  └── MySQL
```

Kubernetes Services provide networking between the application components.

The MySQL database uses persistent storage so that database data is not tied to the lifecycle of an individual MySQL container.

---

# Running the Project

## Start Minikube

```bash
minikube start --driver=docker
```

## Apply Kubernetes manifests

```bash
kubectl apply -f k8s/
```

## Check the cluster

```bash
kubectl get pods
```

```bash
kubectl get services
```

```bash
kubectl get deployments
```

## Check the application rollout

```bash
kubectl rollout status deployment/app
```

---

# Jenkins Requirements

The Jenkins server requires:

* Java 21
* Git
* Docker
* kubectl
* Python 3
* Python virtual environment support
* Jenkins Pipeline support
* SSH Agent Plugin
* GitHub SSH credentials
* Docker Hub credentials

The Jenkins user must also have permission to use Docker and interact with the Kubernetes cluster.

---

# Key DevOps Concepts Practiced

This project provided hands-on experience with:

### Docker

* Building Docker images
* Image tagging
* Docker Hub
* Containerized application deployment

### Jenkins

* Declarative Pipelines
* Pipeline stages
* `when` conditions
* Environment variables
* Jenkins credentials
* Automated testing
* Conditional deployments

### Git

* Git tags
* Versioning
* Remote repositories
* Git diff
* Git history
* Automated release tagging

### Kubernetes

* Deployments
* Services
* Container images
* Rolling updates
* Rollout status
* Image updates using `kubectl set image`
* Basic rollback concepts

### CI/CD

The project demonstrates the complete flow:

```text
Code
 ↓
Test
 ↓
Detect Changes
 ↓
Build
 ↓
Push
 ↓
Deploy
 ↓
Verify
 ↓
Release Tag
```

---

# Known Limitation

The Jenkins pipeline currently updates the live Kubernetes Deployment using:

```bash
kubectl set image
```

This means the image running in the cluster can differ from the image specified in the Kubernetes manifest stored in Git.

For example:

```text
Git repository
deployment.yaml
     │
     │ may contain an older image
     ▼
Kubernetes cluster
     │
     └── Jenkins updates live image directly
```

This is an intentional limitation of this project.

A later project will address configuration consistency and Git as the source of truth using a multi-environment and GitOps approach.

---

# Project Outcome

This project demonstrates a complete Jenkins-driven Kubernetes deployment workflow for a containerized 3-tier application.

The pipeline can automatically:

1. Test application code
2. Detect application changes
3. Generate an application version
4. Build a Docker image
5. Push the image to Docker Hub
6. Update the Kubernetes Deployment
7. Verify the rollout
8. Create a Git release tag

The project builds on the previous Docker + Jenkins project and introduces Kubernetes as the deployment platform.


