# CCCIS_FRIA
First Responder Intelligent Agent

This repository contains proof-of-concept agent for first responders that collects structured tow/intake data using an Agent-driven conversational UI and a Model Context Protocal (MCP) backend server for storing required fields. It includes:

- `src/mcp_servers/towing_server.py` — an MCP server (FastMCP) that exposes tools to read/set
	required towing fields and to return extracted owner-manual chunks.
- `src/` — application frontends and backend:
	- `src/streamlit_app/main.py` — Streamlit UI that talks to a small backend and
		to the MCP server.
	- `src/app/main.py` — a tiny FastAPI backend with endpoints the Streamlit
		front-end calls: `/agent/start`, `/agent/invoke`, `/agent/invoke_towing_guide`.
- `src/mcp_servers/tow_extract.json`, `src/mcp_servers/tow_data.json` — example data files used by the MCP server.

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
    ENDPOINT = 'Azure Endpoint'
    API_VERSION = 'Api version'
    MODEL_NAME = 'GPT model name'
    DEPLOYMENT_NAME = "Azure OpenAI deployment name"

    OPENAI_API_KEY = "openai api key"
    ```


Running the components
----------------------

The project has three cooperating pieces. Run them in separate terminals (or use a process manager):

1. MCP server (towing intake toolset)

    ```bash
	 python src/mcp_servers/towing_server.py
     ```

	 This starts an HTTP MCP server on `127.0.0.1:8765` (the Streamlit UI and
	 example clients connect to this).

2. Backend FastAPI app

	 From the project root go to src directory and run:

     ```bash
	 uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
     ```

	 This exposes the small API the Streamlit app calls:

	 - GET `/agent/start` — returns a new session id.
	 - POST `/agent/invoke` — invoke the agent with a user message + context.
	 - POST `/agent/invoke_towing_guide` — request a towing guide summary.

3. Streamlit UI (If you want to see the new UI run Reflex instead)

	 From the project root go to src directory and run:

     ```bash
	 streamlit run streamlit_app/main.py
     ```

	 Open the URL printed by Streamlit (usually `http://localhost:8501`) and you
	 should see the Tesla Towing Assistant UI. The UI will call the FastAPI backend
	 and the MCP server.

4. Reflex
   
   From the project root go to the Reflex Folder directory and run:
   
   ```bash
	 reflex run
   ```
   And you should see the notification as app is running in the terminal along with the url it's running on.

Tips and troubleshooting
------------------------

- If the Streamlit UI shows errors about contacting the backend, verify
	`BACKEND_URL` is set correctly and reachable from the machine running Streamlit.
- The MCP server reads/writes `tow_data.json` in the repository root. If you
	want to start fresh, delete or edit that file; the MCP server will re-create
	it with defaults.
- If you use OpenAI or another LLM provider, make sure your API key is set in
	the environment and that `app.py` is configured to create an LLM client.

Development notes
-----------------

- The MCP tool wrappers are defined in `towing_server.py` using `fastmcp.FastMCP`.
- The Streamlit app uses `fastmcp.Client` to call MCP tools and a small FastAPI
	backend to encapsulate agent logic. See `src/streamlit_app/main.py` for the
	UI flow and `src/app/main.py` for the simple HTTP endpoints.
