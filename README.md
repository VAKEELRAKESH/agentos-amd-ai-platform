# AgentOS — AMD-Powered Multi-Agent Workflow Console

AgentOS is a production-style AI agent workflow console built for the AMD Developer Hackathon. It enables users to run structured AI workflows through planning, execution, validation, and memory recall using an open-source model served through vLLM on AMD GPU cloud infrastructure.

## What It Does

AgentOS turns a single user prompt into a complete AI workflow:

1. Strategic planning
2. Task execution
3. Quality validation
4. Memory/context recall
5. Final response generation

The system is designed for developers, small software teams, hackathon builders, and AI teams that need reliable, structured AI-assisted workflows instead of simple chatbot responses.

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
