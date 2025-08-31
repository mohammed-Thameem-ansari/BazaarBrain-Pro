# Agents Overview

This doc summarizes the agent modules and where to find detailed references.

## Reality Capture Agent
- File: `agents/reality_capture_agent.py`
- Purpose: OCR via GPT Vision + Gemini Vision, arbitration, and normalization
- Exposes: `process_receipt(image)`, `get_processing_stats()`
- Used by: `backend/routers/receipts.py` (`/api/v1/upload_receipt`, stats)

## Simulation Agent
- File: `agents/simulation_agent.py`
- Purpose: Parse NL queries into scenarios, run what-if simulations, persist results
- Exposes: `simulate(query)`, `get_simulation_stats()`
- Used by: `backend/routers/simulations.py`

## Intake Agent (future)
- File: `agents/intake_agent.py`
- Purpose: Route requests to the correct agent and manage multi-step flows

## Additional Notes
- A separate `ai_agents/` folder contains test harness and sandbox scripts for LLMs.
- For environment variables (OpenAI/Gemini/Supabase), refer to `.env.example`.
- For API endpoints invoking agents, see `docs/BACKEND.md`.
