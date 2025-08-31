import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro")

def categorize_intent(user_input: str) -> dict:
	prompt = f"""
	You are an intent classifier.
	Categorize the following user input into one of these categories:
	1. sales_log
	2. financial_query
	3. general

	Respond only in valid JSON format:
	{{ \"intent\": \"sales_log\" }}
    
	User input: \"{user_input}\"
	"""
	response = model.generate_content(prompt)
	try:
		return json.loads(response.text)
	except Exception:
		return {"intent": "general"}

if __name__ == "__main__":
	tests = [
		"Add today’s milk sales ₹500.",
		"How much profit did I make last month?",
		"Good morning!"
	]
	for t in tests:
		print(t, "→", categorize_intent(t))

CATEGORIES = ["sales_log", "financial_query", "general"]

def categorize_intent(user_input):
	prompt = f"""
	You are an intent classifier.
	Categorize the following user input into one of these categories:
	1. sales_log
	2. financial_query
	3. general

	Respond only in valid JSON format:
	{{ \"intent\": \"sales_log\" }}
    
	User input: \"{user_input}\"
	"""
	try:
		response = model.generate_content(prompt)
		return json.loads(response.text)
	except Exception:
		return {"intent": "general"}


if __name__ == "__main__":
	test_inputs = [
		"Add today’s milk sales ₹500.",
		"How much profit did I make last month?",
		"Good morning!",
		"Log bread sales for today.",
		"Show me last week’s expenses."
	]
	for inp in test_inputs:
		result = categorize_intent(inp)
		print(f"Input: {inp}\nOutput: {result}\n")
