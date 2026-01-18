# mem0-mcp

MCP (Model Context Protocol) server for mem0 memory operations - allows AI agents to store and retrieve memories using Qdrant (vector store) + Neo4j (graph store).

## Overview

This server provides tools for AI agents to perform CRUD operations on mem0 memories, organized by project_id in metadata. It uses:

- **Qdrant**: Vector database for semantic search
- **Neo4j**: Graph database for relational memory storage
- **mem0**: Memory management framework with graph capabilities
- **FastMCP**: MCP server framework

## Local Setup

Follow these comprehensive steps to set up the mem0-mcp server locally.

### Prerequisites

#### 1. Install Docker

**macOS:**
```bash
# Install Docker Desktop for Mac
# Download from https://www.docker.com/products/docker-desktop

# Or install via Homebrew
brew install --cask docker
```

**Linux (Ubuntu/Debian):**
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (to run docker without sudo)
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

**Windows:**
```bash
# Install Docker Desktop for Windows
# Download from https://www.docker.com/products/docker-desktop
# Requires WSL 2 (Windows Subsystem for Linux)
```

#### 2. Verify Docker Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Test Docker installation
docker run hello-world
```

#### 3. Install Python 3.12+

**macOS:**
```bash
# Install via Homebrew
brew install python@3.12

# Verify installation
python3.12 --version
```

**Linux (Ubuntu/Debian):**
```bash
# Add deadsnakes PPA (for latest Python versions)
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

# Install Python 3.12
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev

# Verify installation
python3.12 --version
```

**Windows:**
```bash
# Download Python 3.12+ from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation

# Verify installation
python --version
```

### Setup Steps

#### 1. Clone the Repository

```bash
# Navigate to your projects directory
cd ~/Work/pet-projects

# If you haven't cloned yet, clone the repository
# git clone <repository-url>
cd mem0-mcp/mem0-mcp
```

#### 2. Set Up Environment Variables

Create a `.env` file in the `mem0-mcp` directory with required configuration:

```bash
# Create .env file
touch .env
```

Add the following environment variables to `.env`:

```bash
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Neo4j Configuration
NEO4J_HOST=localhost
NEO4J_PORT=7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=local_neo4j

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=memory

# MCP Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=9000

# Memory Configuration
MEM0_USER_ID=default_user
DEFAULT_PROJECT_ID=default_project_id
```

**Important Notes:**
- Replace `your_openai_api_key_here` with your actual OpenAI API key
- Get your OpenAI API key from https://platform.openai.com/api-keys
- The Neo4j password is `local_neo4j` by default (set in docker-compose.yml)
- Never commit `.env` file to version control

#### 3. Install Python Dependencies (Optional - for local development)

If you want to run the server outside Docker for development:

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install uv for faster dependency management
pip install uv

# Install project dependencies
uv pip install -e .
```

Dependencies installed (from `pyproject.toml`):
- `fastmcp>=2.0.0` - MCP server framework
- `mem0ai[graph]>=0.1.0` - Memory management with graph support
- `qdrant-client>=1.0.0` - Qdrant vector database client

#### 4. Build and Start Docker Containers

The project uses Docker Compose to orchestrate three services:
- **neo4j**: Graph database (ports 7474, 7687)
- **qdrant**: Vector database (ports 6333, 6334)
- **mem0-mcp**: MCP server (port 9000)

```bash
# Make sure you're in the mem0-mcp directory (where docker-compose.yml is located)
cd mem0-mcp

# Build the Docker image
docker compose build

# Start all services in detached mode
docker compose up -d

# View logs (optional)
docker compose logs -f

# To stop watching logs, press Ctrl+C
```

#### 5. Verify Services are Running

```bash
# Check container status
docker compose ps

# You should see three running containers:
# - mem0-mcp-neo4j (healthy)
# - mem0-mcp-qdrant (running)
# - mem0-mcp-server (healthy)

# Check individual service logs
docker compose logs neo4j
docker compose logs qdrant
docker compose logs mem0-mcp
```

#### 6. Access Services

Once all containers are running:

**Neo4j Browser:**
- URL: http://localhost:7474
- Username: `neo4j`
- Password: `local_neo4j`

**Qdrant Dashboard:**
- URL: http://localhost:6333/dashboard

**mem0-mcp Server:**
- URL: http://localhost:9000
- Health check: The container has a built-in healthcheck

#### 7. Test the MCP Server

You can test the MCP server by connecting it to an MCP client or by making HTTP requests:

```bash
# Check if server is responding (from another terminal)
curl http://localhost:9000

# The server should respond with MCP protocol messages
```

### Stopping the Services

```bash
# Stop all containers (preserves data)
docker compose stop

# Stop and remove containers (preserves volumes with data)
docker compose down

# Stop, remove containers, and delete all data volumes (DESTRUCTIVE)
docker compose down -v
```

### Troubleshooting

#### Port Conflicts

If ports are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
# For Neo4j
ports:
  - "7475:7474"  # Change 7474 to 7475
  - "7688:7687"  # Change 7687 to 7688

# For Qdrant
ports:
  - "6335:6333"  # Change 6333 to 6335
  - "6336:6334"  # Change 6334 to 6336

# For mem0-mcp
ports:
  - "9001:9000"  # Change 9000 to 9001
```

Then update the corresponding environment variables in `.env`.

#### Container Startup Issues

```bash
# View detailed logs
docker compose logs -f [service-name]

# Restart a specific service
docker compose restart [service-name]

# Rebuild and restart
docker compose up -d --build --force-recreate
```

#### Neo4j Connection Issues

```bash
# Check Neo4j health
docker compose exec neo4j cypher-shell -u neo4j -p local_neo4j "RETURN 1"

# If authentication fails, you may need to reset Neo4j
docker compose down -v
docker compose up -d
```

#### Qdrant Connection Issues

```bash
# Check Qdrant API
curl http://localhost:6333/collections

# Should return an empty list or list of collections
```

#### OpenAI API Issues

```bash
# Verify your OpenAI API key is valid
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY"
```

### Development Workflow

#### Running Locally (without Docker)

For rapid development, you can run the MCP server locally:

```bash
# Make sure Qdrant and Neo4j containers are running
docker compose up -d neo4j qdrant

# Activate virtual environment
source venv/bin/activate

# Update .env to use localhost for services
# NEO4J_HOST=localhost
# QDRANT_HOST=localhost

# Run the server
python main.py
```

#### Rebuilding After Code Changes

```bash
# Rebuild and restart the mem0-mcp service
docker compose up -d --build mem0-mcp

# View logs
docker compose logs -f mem0-mcp
```

### Data Persistence

The setup uses Docker volumes for data persistence:
- `neo4j_data`: Neo4j database files
- `neo4j_logs`: Neo4j log files
- `qdrant_data`: Qdrant vector storage

Data persists across container restarts. To reset all data:

```bash
# WARNING: This will delete all stored memories
docker compose down -v
docker compose up -d
```

## Available Tools

The mem0-mcp server provides the following MCP tools:

- **add_memory**: Store new information with project organization
- **search_memory**: Find relevant memories using natural language
- **get_memory**: Retrieve a specific memory by ID
- **update_memory**: Modify existing memory content
- **delete_memory**: Remove a memory
- **list_memories**: List all memories for a project

## Architecture

The system uses a hybrid storage approach:

1. **Vector Store (Qdrant)**: Enables semantic search across memories
2. **Graph Store (Neo4j)**: Stores relationships between entities and memories
3. **mem0 Framework**: Orchestrates both stores and provides intelligent memory management
4. **OpenAI LLM**: Used by mem0 for entity/relation extraction (gpt-4o-mini)

## Configuration

All configuration is handled via environment variables (see `.env` file). Key settings:

- **OPENAI_API_KEY**: Required for mem0's LLM features
- **NEO4J_***: Neo4j connection settings
- **QDRANT_***: Qdrant connection settings
- **MCP_***: MCP server settings
- **MEM0_USER_ID**: Default user identifier for memories
- **DEFAULT_PROJECT_ID**: Default project for organizing memories
