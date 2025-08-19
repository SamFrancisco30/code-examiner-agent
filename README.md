# Coding Examienr Agent
[简体中文](./README.zh.md)

> ⚠️ **Warning:** This documentation may contain outdated or incomplete information. Please refer to the source code and configuration files for the most accurate and up-to-date details.

This project is designed to help you leetcode better. Analysis and suggestions about your code and coding would be provided by the agent (maybe it's just a workflow) to improve your knowledge and coding skills.

The prompt of the agent is written in Chinese, so the analysis and suggestions would be given in Chinese too. English version is under development.

## Install Dependencies
The following packages / tools are required to run this project:
- [Node.js](https://nodejs.org/en/download/) (v14+)
- [Python](https://www.python.org/downloads/) (3.10+)
- [pnpm](https://pnpm.io/installation) (recommended package manager)

### Frontend Setup
1. Navigate to the frontend directory:
    ```bash
    cd code-examiner-agent/frontend
    ```
2. Install dependencies:
    ```bash
    pnpm install
    ```
3. Create a `.env` file in the `code-examiner-agent/frontend` directory, following the format in `.env.example`, and fill in the required keys.

### Backend Setup
1. Navigate to the backend directory:
    ```bash
    cd code-examiner-agent/backend
    ```
2. Create and activate a virtual environment:   
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # 或 venv\Scripts\activate  # Windows
    ```
3. Install dependencies:
    ```bash
    pip install fastapi uvicorn pydantic python-multipart openai pika langgraph mcp redis dotenv tenacity
    ```

## Run the Application
### Frontend
1. Navigate to the frontend directory:
    ```bash
    cd code-examiner-agent/frontend
    ```
2. Start the development server:
    ```bash
    pnpm run dev
    ``` 

### Backend
1. Activate the virtual environment if not already activated:
    ```bash
    source backend/venv/bin/activate  # Linux/Mac
    # venv\Scripts\activate  # Windows
    ```
2. Start the backend server:
    ```bash
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ```