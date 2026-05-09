# AgentOS — AMD-Powered Multi-Agent Workflow Console

I built AgentOS for the AMD Developer Hackathon to test how a practical AI agent workflow can run on AMD GPU cloud infrastructure.

The idea is simple: instead of giving only one chatbot-style answer, the system takes a user task and runs it through a structured workflow — planning, execution, validation, and memory recall.

The frontend is built with React and Vite. The backend is built with FastAPI. The model is Mistral 7B served through vLLM on an AMD GPU cloud instance. The backend connects to that vLLM endpoint and returns structured workflow results to the UI.

This project is mainly focused on Track 1: AI Agents & Agentic Workflows.

## What It Does

AgentOS turns a single user prompt into a complete AI workflow:

1. Strategic planning
2. Task execution
3. Quality validation
4. Memory/context recall
5. Final response generation

## Key Features

- Multi-agent workflow pipeline
- AMD vLLM-powered inference
- Mistral 7B model integration
- FastAPI backend
- React frontend
- Workflow routing
- Response validation
- Direct vLLM fallback for reliability
- ChromaDB memory recall
- Production/demo status indicators
- Clean AI operations console UI

## Architecture

```text
React Frontend
      ↓
FastAPI Backend
      ↓
Agent Workflow Layer
      ↓
AMD vLLM Endpoint
      ↓
Mistral 7B Instruct Model
      ↓
Validated Final Response
```

## Tech Stack
- **React** / **Vite**
- **FastAPI** / **Python**
- **CrewAI**-style agent workflow
- **LangChain**-compatible orchestration
- **vLLM**
- **Mistral 7B Instruct**
- **AMD GPU** cloud infrastructure
- **ChromaDB**
- **Framer Motion**

## AMD Usage

The project uses AMD GPU cloud infrastructure to serve an open-source language model through vLLM. The backend connects to the vLLM OpenAI-compatible endpoint and routes user tasks through an agent workflow.

Verified production path:
`Frontend → FastAPI Backend → AMD vLLM → Mistral 7B`

## Agent Workflow

AgentOS uses the following workflow roles:
- **Strategic Planner**
- **Senior Research Analyst**
- **Task Executor**
- **Quality Assurance Validator**

The workflow returns:
- Final answer
- Plan
- Research status
- Validation result
- Workflow status
- Memory recall
- Agents used
- Runtime duration

## Local Setup

### 1. Clone repository
```bash
git clone <your-repo-url>
cd ai-platform
```

### 2. Backend setup
```bash
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.server.safe.txt
```
Create `.env` from `.env.example`.

### 3. Start AMD vLLM tunnel
```bash
ssh -i "$HOME\.ssh\amd-ai-platform" -N -L 8000:localhost:8000 root@YOUR_AMD_INSTANCE_IP
```
Verify: `curl http://127.0.0.1:8000/v1/models`

### 4. Start backend
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8002
```
Verify: `curl http://127.0.0.1:8002/api/v1/agents/info`

### 5. Frontend setup
```cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
Open: `http://127.0.0.1:5173/`

## Demo Prompts
- Create a concise 3-step validation checklist for this AMD AI agent platform. Keep it practical and demo-ready.
- Create a 60-second demo script for AgentOS, an AMD GPU-powered AI agent workflow console.
- Review this AI platform for hackathon readiness and return PASS, PASS_WITH_NOTES, or NEEDS_REVISION.

## Hackathon Track
**Best fit:** Track 1: AI Agents & Agentic Workflows

## Project Status
Final acceptance testing passed after response-quality hardening:
- vLLM endpoint verified
- Backend production mode verified
- Frontend verified
- Multi-agent workflow verified
- Response fallback verified
- No mock placeholder output in final tests

## Future Roadmap
- Google/GitHub authentication
- User-specific workflow history
- Real model switching between Mistral, Llama, and Qwen
- Deployment to public cloud
- Observability and workflow tracing
- Team workspace support
- Advanced multimodal agent workflows
