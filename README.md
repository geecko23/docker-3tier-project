# Docker 3-Tier Application — Multi-Environment Kubernetes + Jenkins CI/CD

A containerized 3-tier Flask application deployed to Kubernetes with separate **development and production environments**, automated testing, Docker image versioning, Jenkins CI/CD, Kustomize configuration management, persistent storage, resource limits, and controlled production promotion.

This project extends the previous Docker + Jenkins + Kubernetes implementation by introducing **multi-environment Kubernetes deployments** and a more controlled CI/CD workflow where Git and Kustomize define the desired application configuration.

---

# Architecture

```text
                              GitHub
                                 │
                                 │ Push
                                 ▼
                         ┌──────────────┐
                         │    Jenkins   │
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              Development              Production
                Pipeline                  Pipeline
                    │                       │
              Test + Build              Manual
                    │                   Promotion
                    │                       │
                    ▼                       │
              Docker Hub ◄──────────────────┘
                    │
                    │ Pull versioned image
                    ▼
             Kubernetes Cluster
                    │
          ┌─────────┴─────────┐
          │                   │
     development          production
      namespace             namespace
          │                   │
     ┌────┼────┐         ┌────┼────┐
     │    │    │         │    │    │
   Nginx Flask Redis    Nginx Flask Redis
          │                   │
        MySQL               MySQL
          │                   │
        PVC                   PVC
```

---

# Application Architecture

The application consists of four main components:

* **Nginx** — reverse proxy and external entry point
* **Flask** — application layer
* **MySQL** — relational database
* **Redis** — visit counter/cache layer

The Flask application communicates with MySQL and Redis through Kubernetes Services.

---

# Technologies

* Docker
* Docker Compose
* Kubernetes
* Minikube
* Kustomize
* Jenkins
* Git & GitHub
* Docker Hub
* Python
* Flask
* MySQL
* Redis
* Nginx
* pytest
* Linux

---

# Project Structure

```text
docker-3tier-project/
│
├── app/
│   ├── app.py
│   ├── requirements.txt
│   ├── test_app.py
│   └── Dockerfile
│
├── db/
│   ├── Dockerfile
│   └── init.sh
│
├── nginx/
│   ├── nginx.conf
│   └── Dockerfile
│
├── k8s/
│   ├── base/
│   │   ├── ...
│   │   └── kustomization.yaml
│   │
│   └── overlays/
│       ├── development/
│       │   ├── ...
│       │   ├── kustomization.yaml
│       │   └── Jenkinsfile
│       │
│       └── production/
│           ├── ...
│           ├── kustomization.yaml
│           └── Jenkinsfile
│
├── compose.yml
├── Jenkinsfile
└── README.md
```

The Kubernetes configuration is organized using a **base + overlays** structure.

```text
                 k8s/base
                    │
          ┌─────────┴─────────┐
          │                   │
   development overlay   production overlay
          │                   │
     Development          Production
```

The base contains common Kubernetes resources, while the overlays contain environment-specific configuration.

---

# Multi-Environment Kubernetes

Project 5 introduces two independent environments:

```text
development
production
```

Each environment runs in its own Kubernetes namespace.

```text
Kubernetes Cluster
│
├── namespace: development
│   ├── app
│   ├── nginx
│   ├── mysql
│   ├── redis
│   └── development PVCs
│
└── namespace: production
    ├── app
    ├── nginx
    ├── mysql
    ├── redis
    └── production PVCs
```

This provides environment isolation while allowing both environments to share the same Kubernetes cluster.

---

# Kustomize

Kustomize is used to manage environment-specific Kubernetes configuration without duplicating the entire set of manifests.

The project uses:

```text
k8s/
├── base/
└── overlays/
    ├── development/
    └── production/
```

The base contains common resources.

The overlays customize environment-specific settings such as:

* Namespace
* Replica counts
* Environment variables
* PersistentVolumeClaims
* Resource limits
* Environment-specific configuration
* Deployment settings

Kustomize builds the final Kubernetes manifests for each environment.

Example:

```bash
kubectl kustomize k8s/overlays/development
```

```bash
kubectl kustomize k8s/overlays/production
```

---

# Environment Configuration

The application receives its database and Redis configuration through Kubernetes configuration.

Example environment variables:

```text
DB_HOST=mysql-service
DB_NAME=appdb
DB_PORT=3306

REDIS_HOST=redis-service
REDIS_PORT=6379
```

The same application can therefore run in both environments while Kubernetes provides the appropriate environment-specific configuration.

---

# Persistent Storage

MySQL uses Kubernetes PersistentVolumeClaims.

Separate storage is used for development and production.

```text
Development
    │
    └── MySQL PVC

Production
    │
    └── MySQL PVC
```

This prevents database data from being tied to the lifecycle of an individual MySQL pod.

---

# Resource Management

Resource requests and limits are defined for Kubernetes workloads.

This provides Kubernetes with information about the resources required by containers and prevents workloads from consuming unlimited resources.

Example concept:

```text
Pod
 │
 ├── CPU request
 ├── CPU limit
 ├── Memory request
 └── Memory limit
```

Production and development can have different resource configurations through their Kustomize overlays.

---

# CI/CD Architecture

Project 5 uses separate Jenkins pipelines for development and production.

```text
                         GitHub
                            │
                            ▼
                    ┌──────────────┐
                    │ Jenkins      │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
        Development                Production
          Pipeline                  Pipeline
              │                         │
       Automatic trigger           Manual trigger
              │                         │
          Test code                    │
              │                         │
        Build image                   │
              │                         │
        Push to Docker Hub             │
              │                         │
       Deploy to Dev                  │
              │                         │
       Verify rollout                 │
              │                         │
              └──────────┬──────────────┘
                         │
                  Tested image
                         │
                         ▼
                  Production
                   promotion
```

---

# Development Pipeline

The development pipeline is automatically triggered when application-related changes are detected.

The general flow is:

```text
GitHub Push
     │
     ▼
SCM Change Detection
     │
     ▼
Run Tests
     │
     ▼
Determine Version
     │
     ▼
Build Docker Image
     │
     ▼
Push Image to Docker Hub
     │
     ▼
Deploy to Development
     │
     ▼
Wait for Rollout
     │
     ▼
Verify Deployment
```

Application versions use a common artifact naming scheme such as:

```text
app-v1
app-v2
app-v3
...
```

A new application image is built when application code changes.

---

# SCM Trigger Filtering

The development pipeline does not run a complete deployment for every repository change.

The pipeline uses SCM filtering so that application changes trigger the application CI/CD workflow.

Relevant changes include:

```text
app/**
Dockerfile
```

Changes that do not affect the application do not unnecessarily trigger the application build and deployment process.

This reduces unnecessary builds and deployments.

---

# Production Pipeline

Production is deliberately separated from the development pipeline.

Production deployment is a controlled promotion process rather than an automatic build of a new image.

```text
Development
     │
     ▼
Build app-vN
     │
     ▼
Test
     │
     ▼
Deploy to Development
     │
     ▼
Verify
     │
     ▼
Approved artifact
     │
     ▼
Production Promotion
     │
     ▼
Deploy the SAME app-vN
```

The production pipeline therefore promotes an already-built and tested application image rather than rebuilding the application.

This follows the principle:

> **Build once, promote the same artifact.**

---

# Artifact Versioning

Application Docker images are versioned independently of Jenkins build numbers.

Example:

```text
app-v1
app-v2
app-v3
```

The same artifact can move through environments:

```text
Docker Hub
    │
    └── app-v3
          │
          ├── Development
          │
          └── Production
```

This ensures that production runs the exact application artifact that was tested in development.

---

# Git as the Source of Truth

Project 5 moves away from directly modifying the running Kubernetes Deployment with:

```bash
kubectl set image
```

Instead, Kubernetes configuration is managed through the repository's Kustomize configuration.

The desired state is represented in Git:

```text
Git Repository
      │
      ▼
Kustomize configuration
      │
      ▼
Kubernetes desired state
      │
      ▼
Running workloads
```

This keeps Kubernetes configuration version-controlled and makes environment configuration easier to review and reproduce.

---

# Kubernetes Deployment

The application runs on a local Minikube Kubernetes cluster.

Each environment contains its own application stack.

```text
Development Namespace
│
├── Nginx
├── Flask
├── Redis
└── MySQL
     │
     └── Persistent Storage


Production Namespace
│
├── Nginx
├── Flask
├── Redis
└── MySQL
     │
     └── Persistent Storage
```

Production uses multiple Flask application replicas to provide basic horizontal scaling.

---

# Kubernetes Services

Kubernetes Services provide stable networking between components.

For example:

```text
Flask
 │
 ├── mysql-service:3306
 │
 └── redis-service:6379
```

The application does not need to know the individual pod IP addresses.

Kubernetes Services provide stable DNS-based endpoints inside the cluster.

---

# Health and Reliability

The Kubernetes deployment uses health checks to allow Kubernetes to determine whether application containers are ready to receive traffic and whether unhealthy containers need to be restarted.

The project also practices:

* Rolling updates
* Rollout monitoring
* Pod health inspection
* Container logs
* Service inspection
* Deployment status
* Basic failure troubleshooting

---

# Running the Project

## Start Minikube

The project can be run on a local Minikube cluster.

Example:

```bash
minikube start
```

The exact Minikube driver depends on the local environment.

---

## Deploy Development

Build and apply the development configuration:

```bash
kubectl apply -k k8s/overlays/development
```

Check the namespace:

```bash
kubectl get all -n development
```

Check persistent storage:

```bash
kubectl get pvc -n development
```

Check rollout:

```bash
kubectl rollout status deployment/app -n development
```

---

## Deploy Production

Apply the production configuration:

```bash
kubectl apply -k k8s/overlays/production
```

Check the namespace:

```bash
kubectl get all -n production
```

Check persistent storage:

```bash
kubectl get pvc -n production
```

Check rollout:

```bash
kubectl rollout status deployment/app -n production
```

---

# Useful Kubernetes Commands

Check all pods:

```bash
kubectl get pods -A
```

Check deployments:

```bash
kubectl get deployments -A
```

Check services:

```bash
kubectl get services -A
```

Check persistent volume claims:

```bash
kubectl get pvc -A
```

Describe a pod:

```bash
kubectl describe pod <pod-name> -n <namespace>
```

View pod logs:

```bash
kubectl logs <pod-name> -n <namespace>
```

Follow logs:

```bash
kubectl logs -f <pod-name> -n <namespace>
```

Check deployment status:

```bash
kubectl rollout status deployment/<deployment-name> -n <namespace>
```

Check rollout history:

```bash
kubectl rollout history deployment/<deployment-name> -n <namespace>
```

---

# Jenkins Requirements

The Jenkins environment requires:

* Java 21
* Git
* Docker
* kubectl
* Python 3
* Python virtual environment support
* Jenkins Pipeline support
* Jenkins credentials
* SSH access to GitHub
* Docker Hub credentials
* Access to the Kubernetes cluster

The Jenkins user must have the required permissions to execute Docker, Git, kubectl, and the project's CI/CD commands.

---

# Key DevOps Concepts Practiced

## Docker

* Docker image creation
* Docker image tagging
* Docker Hub
* Containerized application deployment
* Multi-container applications

## Jenkins

* Declarative Pipelines
* Multiple pipelines
* Pipeline stages
* Conditional execution
* Jenkins credentials
* Automated testing
* SCM triggers
* Development and production workflows

## Git

* Git branches
* Git commits
* Git history
* Git tags
* Versioned infrastructure configuration
* Git as a source of truth

## Kubernetes

* Pods
* Deployments
* Services
* Namespaces
* ConfigMaps
* Secrets
* PersistentVolumeClaims
* Resource requests and limits
* Rolling updates
* Health checks
* Multi-replica deployments
* Kubernetes networking
* Cluster troubleshooting

## Kustomize

* Base configuration
* Environment overlays
* Patches
* Environment-specific configuration
* Manifest generation

## CI/CD

The project demonstrates:

```text
Code Change
     │
     ▼
SCM Detection
     │
     ▼
Test
     │
     ▼
Build
     │
     ▼
Push Image
     │
     ▼
Development Deployment
     │
     ▼
Verify
     │
     ▼
Promote Same Artifact
     │
     ▼
Production Deployment
```

---

# Project Evolution

This project is part of a progression from a simple containerized application toward a production-oriented DevOps workflow.

```text
Project 1
Dockerized 3-Tier Application
        │
        ▼
Project 2
Jenkins CI/CD
        │
        ▼
Project 3
Kubernetes Deployment
        │
        ▼
Project 4
Kubernetes + Jenkins CI/CD
        │
        ▼
Project 5
Multi-Environment Kubernetes
+ Kustomize
+ Artifact Promotion
+ Production Workflow
```

Project 5 focuses on introducing the operational concepts required when the same application must exist in multiple environments with controlled promotion between them.

---

# Project Outcome

Project 5 demonstrates a complete multi-environment Kubernetes deployment workflow.

The project now supports:

1. Containerized 3-tier application deployment
2. Kubernetes-based application management
3. Development and production environments
4. Namespace isolation
5. Kustomize base and overlays
6. Environment-specific configuration
7. Persistent database storage
8. Kubernetes resource limits
9. Automated development CI/CD
10. Controlled production promotion
11. Versioned Docker artifacts
12. Build-once, promote-same-artifact workflow
13. SCM change filtering
14. Rolling deployments
15. Kubernetes health and rollout verification
16. Git-managed Kubernetes configuration

The result is a more realistic DevOps workflow where application code, infrastructure configuration, deployment environments, and release artifacts are managed in a controlled and reproducible way.

---

# Future Improvements

Possible future improvements include:

* GitOps with Argo CD
* Monitoring with Prometheus and Grafana
* Centralized logging
* Infrastructure provisioning with Terraform
* Deployment to AWS
* Managed Kubernetes with Amazon EKS
* Production-grade ingress and TLS
* Automated rollback strategies
* More comprehensive observability

