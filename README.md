# CCCIS_FRIA
First Responder Intelligent Agent

This repository contains proof-of-concept agent for first responders that collects structured tow/intake data using an Agent-driven conversational UI and a Model Context Protocal (MCP) backend server for storing required fields. It includes:

- `src/mcp_servers/towing_server.py` — an MCP server (FastMCP) that exposes tools to read/set
	required towing fields and to return extracted owner-manual chunks.
- `src/` — application frontends and backend:
- `src/app/main.py` — a tiny FastAPI backend with endpoints the Streamlit
		front-end calls: `/agent/start`, `/agent/invoke`, `/agent/invoke_towing_guide`.

Quick start (Linux / macOS/ windows)
--------------------------+

1. Clone the repository:
    ```bash
	 git clone https://github.com/DePaulIDLab/CCCIS_FRIA.git
	 cd CCCIS_FRIA
     ```

2. Create and activate a Python virtual environment (recommended)

    ```bash
	 python3 -m venv .venv
	 source .venv/bin/activate
     ```

3. Install `uv` for faster dependency installation.

    ```bash
    pip install uv
    ```

4. Install dependencies. You can use pip with the existing `requirements.txt`,:

    ```bash
	uv pip install -r requirements.txt
    ```

5. Adding or removing dependencies using `uv`

    ```bash
    ## add a dependency
    uv add [DEPENDENCY-NAME]

    ## remove a dependency
    uv remove [DEPENDENCY-NAME]
    ```

6. Setting up Environment variables

    Create `.env` file at root directory level. And add these env variables along with values.

    ```bash
    ENDPOINT=""
 
    API_VERSION=""
    
    
    AZURE_OPENAI_API_KEY=""
    DEPLOYMENT_NAME=""
    MODEL_NAME=""
    MCP_URL=""
    MCP_PORT=""
    
    BACKEND_URL=""
    
    AZURE_SPEECH_REGION=""
    AZURE_SPEECH_KEY=""

    # PostgreSQL Database
    DATABASE_URL = ""
    ```

7. Run this only once you cloned the repository(only one time). To setup the database with seed data run the below command

    ```bash
    python3 -m src.database.check_for_tables_or_seed_create
    ```
Running the components
----------------------

The project has three cooperating pieces. Run them in separate terminals (or use a process manager):

1. Create tables with seed data.

Run the below command to check if the tables are ctreated or not, if not created it will create the necessary tables with seed data.

    ```bash
    python3 -m src.database.check_for_tables_or_seed_create
    ```
    or 
    ```bash
    python3 src/database/check_for_tables_or_seed_create.py
    ```

2. MCP server (towing intake toolset)

    ```bash
	 python src/mcp_servers/towing_server.py
     ```

	 This starts an HTTP MCP server on `127.0.0.1:8765` (the Streamlit UI and
	 example clients connect to this).

3. Backend FastAPI app

	 From the project root go to src directory and run:

     ```bash
	 uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
     ```

	 This exposes the small API the Streamlit app calls:

	 - GET `/agent/start` — returns a new session id.
	 - POST `/agent/invoke` — invoke the agent with a user message + context.
	 - POST `/agent/invoke_towing_guide` — request a towing guide summary.


