# BazaarBrain-Pro – Project Plan

## Vision
An AI-powered collective bargaining and financial intelligence platform for small shopkeepers.  
Our goal: help small retailers digitize their sales, analyze profitability, and unlock collective buying power.

## Hackathon Goals
- Build a working prototype in 2 weeks.
- Integrate OpenAI GPT + Google Gemini for complementary strengths.
- Demonstrate unique value: reality capture (OCR + voice), intelligent simulation, and collective bargaining.

## Key Features
1. **Intake Agent** – Classifies inputs (sales logs, financial queries, general tasks).  
2. **Reality Capture Agent** – Extracts structured data from images, receipts, and voice.  
3. **Simulation Agent** – Models sales/profit and runs “what-if” scenarios.  
4. **Explain Agent** – Turns raw AI output into shopkeeper-friendly insights.  
5. **Collective Bargaining Simulation** – Aggregates multiple orders for better supplier deals.  
6. **Voice Input & Output** – Speak queries and receive spoken answers.  
7. **Multi-user Accounts & Auth** – Secure access for different shopkeepers.  

## Tech Stack
- **AI & GenAI**
  - OpenAI GPT-4o (reasoning, language understanding).
  - Google Gemini Pro + Gemini Vision (structured reasoning, multimodal).
- **Backend**
  - FastAPI (Python)
  - Supabase (database + auth)
- **Frontend**
  - Next.js (React, TailwindCSS)
  - ShadCN UI
- **DevOps**
  - GitHub Actions (CI/CD)
  - Vercel (Frontend hosting)
  - Render/Heroku (Backend hosting)
- **Other**
  - Whisper (Speech-to-Text, if needed)
  - TTS APIs (OpenAI or Google Cloud TTS)

## Team Roles
- **You (AI Lead)** – AI agent creation, prompts, model integration.  
- **Fairoz Ahmed (Backend Lead)** – API endpoints, Supabase integration, orchestration.  
- **Suriya (Frontend & Design)** – UI/UX, dashboards, visualizations.  
- **ChatGPT (AI Buddy)** – Guidance, code templates, project structuring.

## Milestones
- **M1: Kickoff & Repo Setup**
- **M2: Environment & API Setup**
- **M3: Core Agents**
- **M4: UI & Integration**
- **M5: Testing & Polish**
