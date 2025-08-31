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

## Database Integration Workflows

### Reality Capture Agent Database Flow

1. **Image Processing**: Agent processes receipt/bill images using dual LLM OCR
2. **Result Arbitration**: Applies intelligent arbitration logic to combine GPT + Gemini outputs
3. **Automatic Storage**: Automatically calls `db.save_transaction()` with:
   - `user_id`: Extracted from JWT token
   - `raw_input`: Original image path/filename
   - `parsed_json`: Structured OCR results
   - `source`: Processing source type (image, receipt, bill)
4. **Transaction ID**: Returns transaction ID for future reference
5. **Error Handling**: Gracefully handles database failures with fallback logging

### Simulation Agent Database Flow

1. **Query Processing**: Agent parses natural language business queries using dual LLMs
2. **Parameter Extraction**: Extracts structured parameters (scenario, item, change, etc.)
3. **Simulation Execution**: Runs mathematical simulations based on extracted parameters
4. **Automatic Storage**: Automatically calls `db.save_simulation()` with:
   - `user_id`: Extracted from JWT token
   - `query`: Original natural language query
   - `parameters`: Structured simulation parameters
   - `result`: Complete simulation results and analysis
5. **Simulation ID**: Returns simulation ID for future reference
6. **Error Handling**: Gracefully handles database failures with fallback logging

### Database Schema Integration

Both agents integrate with the following database tables:

- **`transactions`**: Stores OCR results with user association
- **`simulations`**: Stores business simulation queries and results
- **`users`**: Links all data to authenticated user accounts

### Error Handling and Fallbacks

- **Database Unavailable**: Agents continue processing with local result storage
- **Save Failures**: Results logged locally with error tracking
- **Partial Failures**: Graceful degradation with available functionality
- **User Feedback**: Clear error messages and status reporting
