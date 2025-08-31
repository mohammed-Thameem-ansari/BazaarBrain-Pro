# BazaarBrain-Pro – AI Agents

## Agent Architecture

BazaarBrain uses a multi-agent system where each agent specializes in specific business intelligence tasks, working together to provide comprehensive insights for shopkeepers.

## Agent Descriptions

### Intake Agent
Classifies and routes incoming requests (sales logs, financial queries, general business questions) to the appropriate specialized agent. Acts as the intelligent dispatcher for all user interactions.

### Reality Capture Agent v2
Extracts structured data from receipts, bills, and handwritten notes using dual LLM orchestration (GPT-4o Vision + Gemini Pro Vision). Features intelligent arbitration logic to resolve conflicts between different AI interpretations, ensuring maximum accuracy in data extraction. Includes image preprocessing, structured JSON output, and comprehensive result logging.

### Simulation Agent (MVP)
Handles business "what-if" scenarios through natural language query parsing and mathematical simulation. Supports price increase/decrease analysis, bulk order scenarios, and profit impact calculations. Uses dual LLM parsing with arbitration, sample business data integration, and provides actionable business recommendations with detailed assumptions.

### Explain Agent
Translates complex AI outputs into simple, actionable insights that shopkeepers can easily understand. Converts technical analysis into practical business recommendations and clear next steps.

### Arbitration Panel Agent
Coordinates collective bargaining simulations by aggregating multiple shopkeeper orders and negotiating with suppliers. Manages group purchasing decisions and ensures fair distribution of benefits.

## Routing Logic

The Intake Agent intelligently routes requests based on input type and content:

- **Image Inputs** → Reality Capture Agent (OCR processing)
- **"What if" Queries** → Simulation Agent (business scenarios)
- **Sales Data** → Sales Agent (future implementation)
- **Financial Queries** → Financial Agent (future implementation)
- **General Questions** → General Business Assistant

### Dual LLM Arbitration
Both Reality Capture and Simulation agents use dual LLM processing with intelligent arbitration:
- **GPT + Gemini Agreement** → Use confirmed result
- **Single LLM Success** → Use available result
- **Conflicting Results** → Merge or prefer more detailed output
- **Both Failed** → Fallback to basic parsing
