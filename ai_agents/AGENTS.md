# AI Agents Blueprint

This document defines the agents in BazaarBrain Pro, specifying their inputs, outputs, and example prompts. This serves as a contract between frontend, backend, and AI.

---

## 1. Intake Agent

**Purpose:** Categorizes user requests into an intent.

**Inputs:**
- `user_message`: string (free text typed by the user)

**Outputs:**
```json
{ "intent": "sales_log" }
```

**Possible intents:**
- "sales_log"
- "financial_query"
- "general"

**Example prompt:**
> Classify the user message into one of: [sales_log, financial_query, general].
> User: "Add today’s milk sales"
> Response: { "intent": "sales_log" }

---

## 2. Reality Capture Agent (OCR Agent)

**Purpose:** Extracts data from receipts/bills using OCR.

**Inputs:**
- `receipt_image`: base64 or file path

**Outputs:**
```json
{
  "date": "2025-08-27",
  "items": [
    { "name": "Milk", "quantity": 2, "price": 40 },
    { "name": "Bread", "quantity": 1, "price": 25 }
  ],
  "total": 105
}
```

**Example prompt:**
> Extract structured data from this shop receipt image.

---

## 3. Simulation Agent

**Purpose:** Simulates financial/business outcomes (e.g., “What if sales increase 20%?”, bulk order savings, price changes).

**Inputs:**
- `scenario_description`: string (user’s what-if question, e.g., "What if I increase rice price by 5%?" or "Order 200 rice in bulk")
- `historical_data`: JSON (sales records)

**Outputs (structured):**
```json
{
  "scenario": "price_increase|price_decrease|bulk_order|quantity_change|cost_change",
  "item": "Rice",
  "change": "+5%",
  "before": { "revenue": 1000, "profit": 200, "quantity": 100, "price": 10 },
  "after": { "revenue": 1050, "profit": 210, "quantity": 98, "price": 10.5 },
  "impact": { "revenue_change": 50, "profit_change": 10, "percentage_change": 5 },
  "recommendations": ["Consider gradual changes"],
  "assumptions": ["Elasticity ~ -0.2"],
  "confidence": 82
}
```

The agent arbitrates between GPT and Gemini outputs and returns a consistent JSON. For bulk orders, it includes savings/cost effects and may include revenue/profit fields.

Offline fallback: if DB persistence fails, the agent logs a local marker and returns results to the caller without blocking the user.

**Example prompt:**
> Given this sales history JSON, simulate what happens if sales increase by 20%.

---

## 4. Explain Agent

**Purpose:** Explains financial terms or results in simple words.

**Inputs:**
- `question`: string

**Outputs:**
```json
{ "explanation": "Revenue is the money you earn from sales before subtracting costs." }
```

**Example prompt:**
> Explain in simple words: "What is revenue vs profit?"

---

## 5. Bargain Agent

**Purpose:** Aggregates shopkeepers’ purchase orders to get bulk discounts.

**Inputs:**
- `orders`: JSON (list of multiple shopkeeper orders)

**Outputs:**
```json
{
  "aggregate_order": [
    { "item": "Rice", "quantity": 50 },
    { "item": "Sugar", "quantity": 30 }
  ],
  "negotiation_strategy": "Buy in bulk, ask for 10% discount"
}
```

**Example prompt:**
> Combine these orders from different shopkeepers into one bulk order and suggest a bargaining strategy.

Day 7 TODOs:
- Add role-based access controls to sensitive agent actions.
- Persist collective participants per product and surface in outputs.
- Integrate Reality Capture-derived stock levels into SimulationAgent assumptions.

---

## 6. Arbitration Agent

**Purpose:** Compares answers from GPT and Gemini → chooses best one.

**Inputs:**
- `gpt_answer`: string
- `gemini_answer`: string

**Outputs:**
```json
{
  "final_answer": "Gemini’s answer chosen because it was more detailed."
}
```

**Example prompt:**
> Compare these two answers. Pick the clearer and more useful one for a shopkeeper.

