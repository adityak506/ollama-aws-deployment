# 🚀 Deploying Open-Source LLMs on AWS EC2 with Ollama & FastAPI

An end-to-end, production-ready solution to self-host and serve open-source Large Language Models (e.g., Llama 3.2, Mistral, DeepSeek) on **AWS EC2** using **Ollama**, wrapped with a high-performance **FastAPI** REST API, orchestrated via **Docker Compose**, and tested with an interactive **Streamlit** client.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Prerequisites](#-prerequisites)
- [Step-by-Step AWS EC2 Deployment](#-step-by-step-aws-ec2-deployment)
  - [Step 1: Launch an AWS EC2 Instance](#step-1-launch-an-aws-ec2-instance)
  - [Step 2: Configure Security Groups](#step-2-configure-security-groups)
  - [Step 3: Connect via SSH](#step-3-connect-via-ssh)
  - [Step 4: Clone & Automated Deployment](#step-4-clone--automated-deployment)
  - [Step 5: Verify the Deployment](#step-5-verify-the-deployment)
- [Local Client Setup (Streamlit)](#-local-client-setup-streamlit)
- [Consumption in Python Applications](#-consumption-in-python-applications)
- [Advanced Configuration](#-advanced-configuration)
  - [Enabling GPU Acceleration](#enabling-gpu-acceleration)
  - [Managing Multiple Models](#managing-multiple-models)
  - [Useful Maintenance Commands](#useful-maintenance-commands)
- [License & Acknowledgments](#-license--acknowledgments)

---

## 📖 Overview

Proprietary LLM APIs (such as OpenAI or Google Gemini) charge per token and send sensitive data to third-party servers. This project allows you to:
- **Take 100% control over data privacy** by hosting models inside your own cloud infrastructure.
- **Eliminate recurring per-token inference charges** by running open-source LLMs on self-hosted compute.
- **Expose standard REST endpoints** using FastAPI so that your frontend, LangChain agents, or microservices can consume the models seamlessly.

---

## 🏛️ Architecture

```mermaid
flowchart LR
    subgraph Local["Local Machine / Client"]
        UI["Streamlit Web UI\n(:8501)"]
        ClientApp["Python Scripts / LangChain"]
    end

    subgraph AWS["AWS Cloud (EC2 Instance)"]
        subgraph DockerNetwork["Docker Bridge Network"]
            FastAPI["FastAPI Application\n(:8000)\nReverse Proxy / API Layer"]
            Ollama["Ollama Engine\n(:11434)\nModel Execution & Cache"]
            Volume[("Ollama Volume\n/root/.ollama")]
        end
    end

    UI -->|HTTP Requests| FastAPI
    ClientApp -->|HTTP Requests| FastAPI
    FastAPI -->|Async HTTP (httpx)| Ollama
    Ollama --- Volume
```

---

## ✨ Key Features

- **Automated Bootstrapping (`setup.sh`)**: Single-script deployment that detects OS, installs Docker & Docker Compose, starts services, and pulls your chosen model.
- **Docker Compose Orchestration**: Manages both the Ollama runtime and the FastAPI application with persistent model volumes and automatic restarts.
- **Asynchronous API**: Built with **FastAPI** and **httpx** for non-blocking I/O and optimal throughput during LLM inference.
- **Health Checks & Dynamic Model Discovery**: Endpoints to check server status and inspect all currently downloaded models.
- **Streamlit Interactive UI**: Ready-to-use frontend for prompt testing, model switching, and real-time response generation.

---

## 📂 Project Structure

```text
.
├── app.py                     # FastAPI application serving the LLM endpoints
├── streamlit_app.py           # Streamlit client for testing model inference
├── setup.sh                   # Automated EC2 bootstrap and setup script
├── Dockerfile                 # Docker build configuration for FastAPI service
├── docker-compose.yml         # Multi-container orchestration (Ollama + FastAPI)
├── requirements.txt           # Python backend dependencies
├── pyproject.toml             # Project metadata and configuration
├── docker-compose-explained.txt # Detailed explanation of docker-compose file
├── setup-sh-explained.txt     # Detailed explanation of the setup script
└── projectflow.txt            # Step-by-step deployment guide & notes
```

---

## 🔌 API Endpoints

The FastAPI server exposes the following endpoints on port `8000`:

| Method | Endpoint | Description | Sample Request / Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API status and route directory | `{"message": "Ollama API is running", ...}` |
| `GET` | `/health` | Connectivity check to Ollama server | `{"status": "healthy", "models": [...]}` |
| `GET` | `/models` | List of models currently installed in Ollama | `{"models": [{"name": "llama3.2:latest", ...}]}` |
| `POST` | `/generate` | Generate text completions for a prompt | **Body**: `{"prompt": "Hello", "model": "llama3.2"}` |

---

## 🛠️ Prerequisites

1. **AWS Account** with permissions to launch EC2 instances and manage Security Groups.
2. **SSH Key Pair (`.pem`)** downloaded from AWS.
3. **Local Machine**: Python 3.10+ and Git installed.

---

## 🚀 Step-by-Step AWS EC2 Deployment

### Step 1: Launch an AWS EC2 Instance

1. Navigate to the **AWS Management Console** → **EC2** → **Launch Instance**.
2. **Name**: `my-ollama-server`
3. **OS Image (AMI)**: `Ubuntu Server 24.04 LTS` (or `22.04 LTS`).
4. **Instance Type**:
   - **CPU-only testing**: `t3.large` (2 vCPU, 8 GB RAM) or `t3.xlarge` (4 vCPU, 16 GB RAM).
   - **GPU production**: `g4dn.xlarge` (1 NVIDIA T4 GPU) or `g5.xlarge` (1 NVIDIA A10G GPU).
5. **Key Pair**: Select or create an RSA key pair (e.g., `my-ollama-key.pem`).
6. **Storage**: Minimum **30 GB gp3** SSD (LLM weights require sufficient disk storage).

---

### Step 2: Configure Security Groups

Attach a Security Group with the following inbound rules:

| Type | Port | Source | Purpose |
| :--- | :--- | :--- | :--- |
| **SSH** | `22` | `My IP` | Secure SSH terminal access |
| **Custom TCP** | `8000` | `Anywhere (0.0.0.0/0)` or `My IP` | FastAPI endpoints (consumed by clients) |
| **Custom TCP** | `11434` | `My IP` *(Optional)* | Direct Ollama debugging (keep private in production) |

---

### Step 3: Connect via SSH

Open your terminal or Git Bash and connect to the instance:

```bash
# Set appropriate permissions for key file (Linux / macOS / Git Bash)
chmod 400 my-ollama-key.pem

# SSH into the EC2 instance
ssh -i my-ollama-key.pem ubuntu@<EC2_PUBLIC_IP>
```

---

### Step 4: Clone & Automated Deployment

Once connected to your EC2 instance, install Git, clone your repository, and execute the automated setup:

```bash
# Update packages and install git
sudo apt update && sudo apt install git -y

# Clone your repository
git clone https://github.com/<your-username>/ollama-aws-deployment.git
cd ollama-aws-deployment

# Make setup script executable and run with your desired model
chmod +x setup.sh
sudo bash ./setup.sh --model llama3.2
```

> **What does `setup.sh` do automatically?**
> 1. Detects OS and installs Docker Engine & Docker Compose plugin.
> 2. Sets up directory structure and configures ports.
> 3. Launches the Ollama and FastAPI containers via Docker Compose.
> 4. Waits for Ollama to become healthy and pulls the specified model (`llama3.2`).
> 5. Outputs public API URLs and verification instructions.

---

### Step 5: Verify the Deployment

Run these checks from your local terminal or browser:

```bash
# 1. Health check
curl http://<EC2_PUBLIC_IP>:8000/health

# 2. List downloaded models
curl http://<EC2_PUBLIC_IP>:8000/models

# 3. Test text generation
curl -X POST http://<EC2_PUBLIC_IP>:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2",
    "prompt": "Explain Cloud Computing in 2 sentences."
  }'
```

---

## 💻 Local Client Setup (Streamlit)

You can run an interactive chat interface locally that connects to your deployed EC2 LLM:

1. **Clone the repository locally**:
   ```bash
   git clone https://github.com/<your-username>/ollama-aws-deployment.git
   cd ollama-aws-deployment
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt streamlit requests
   ```

4. **Configure your EC2 Public IP**:
   Open `streamlit_app.py` and update the `API_URL`:
   ```python
   API_URL = "http://<EC2_PUBLIC_IP>:8000"
   ```

5. **Start the Streamlit application**:
   ```bash
   streamlit run streamlit_app.py
   ```
   Open `http://localhost:8501` in your browser, select your model, and start prompting!

---

## 🐍 Consumption in Python Applications

You can easily integrate your deployed LLM endpoint into any Python backend or LangChain pipeline:

```python
import requests

EC2_PUBLIC_IP = "YOUR_EC2_PUBLIC_IP"
API_URL = f"http://{EC2_PUBLIC_IP}:8000/generate"

payload = {
    "model": "llama3.2",
    "prompt": "What are the advantages of self-hosting LLMs?"
}

response = requests.post(API_URL, json=payload, timeout=120)

if response.status_code == 200:
    data = response.json()
    print("LLM Response:\n", data.get("response"))
else:
    print(f"Error {response.status_code}: {response.text}")
```

---

## ⚙️ Advanced Configuration

### Enabling GPU Acceleration

For GPU instances (e.g., `g4dn.xlarge` or `g5.xlarge`):
1. Install NVIDIA drivers and NVIDIA Container Toolkit on the host.
2. In `docker-compose.yml`, uncomment the GPU reservation block:
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: all
             capabilities: [gpu]
   ```
3. Restart the container stack:
   ```bash
   docker compose up -d --force-recreate
   ```

### Managing Multiple Models

You can download and serve additional models without restarting the stack:

```bash
# Pull an additional model inside the Ollama container
docker exec -it ollama ollama pull mistral
docker exec -it ollama ollama pull phi3

# List all models currently resident
docker exec -it ollama ollama list
```
The FastAPI `/models` endpoint and the Streamlit dropdown will automatically detect newly pulled models.

### Useful Maintenance Commands

```bash
# View real-time logs from both services
docker compose logs -f

# View logs for API container specifically
docker logs -f ollama-api

# Stop all running containers
docker compose down

# Start containers in background
docker compose up -d

# Check running container statuses
docker ps
```

---

## 🛡️ Security Best Practices for Production

- **Keep Port 11434 Closed to the Public**: Only expose port `8000` (FastAPI). Ollama should communicate with FastAPI over the internal Docker network.
- **Add Authentication**: Implement API key authentication or OAuth2 tokens in `app.py` before exposing the API over the public internet.
- **Enable HTTPS**: Place an AWS Application Load Balancer (ALB) or Nginx reverse proxy with SSL certificates (Let's Encrypt / AWS Certificate Manager) in front of port `8000`.
- **EIP (Elastic IP)**: Attach an Elastic IP to your EC2 instance so the IP address remains persistent across instance stops and starts.

---

## 📜 License & Acknowledgments

- Built using [Ollama](https://ollama.com/), [FastAPI](https://fastapi.tiangolo.com/), and [Streamlit](https://streamlit.io/).
- Distributed under the MIT License.

