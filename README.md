# CCCIS_FRIA
First Responder Intelligent Agent

This repository contains proof-of-concept agent for first responders that collects structured tow/intake data using an Agent-driven conversational UI and a Model Context Protocal (MCP) backend server for storing required fields. It includes:

Quick start (Linux / macOS/ windows)

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
    # Frontend Configuration
    FRONTEND_URL=""

    # Azure OpenAI Configuration
    ENDPOINT=""
    API_VERSION=""
    AZURE_OPENAI_API_KEY=""
    DEPLOYMENT_NAME=""
    MODEL_NAME=""
    
    # Azure Speech-to-Text
    AZURE_SPEECH_REGION=""
    AZURE_SPEECH_KEY=""

    # PostgreSQL Database
    DATABASE_URL = ""

    # MongoDB Configuration
    MONGODB_URI=""
    ```

7. Run this only once you cloned the repository(only one time). To setup the database with seed data run the below command

    ```bash
    python3 -m src.database.check_for_tables_or_seed_create
    ```
    or 
    ```bash
    python3 src/database/check_for_tables_or_seed_create.py
    ```

8. Backend FastAPI app

	 From the project root go to src directory and run:

     ```bash
	 uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
     ```

9. To get list of endpoints/payloads/schema, use this link to get FastAPI SwaggerUI

    `http://127.0.0.1:8000/docs`


10. Important, since we are using pylint workflow to check the code quality for every push, before pushing the code, run this command to check for any PEP violations. if there are any warnings fix them, for any excpetions you want to avoid, disable those by adding the main warning in the disable section under [MESSAGE CONTROL].

    ```bash
    pylint $(git ls-files '*.py')
    ```

