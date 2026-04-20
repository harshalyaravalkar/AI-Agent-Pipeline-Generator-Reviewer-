# AI Agent Pipeline (Generator + Reviewer)

## Overview
This project implements a simple agent-based system for generating and reviewing educational content based on a given grade and topic.

It consists of two AI agents:
- A Generator Agent that creates explanations and MCQs
- A Reviewer Agent that evaluates the generated content

A refinement loop ensures improved output if issues are detected.

---

## Architecture

### 1. Generator Agent
- **Input:** Grade, Topic  
- **Output:** Structured JSON containing:
  - Explanation
  - 3 Multiple Choice Questions (MCQs)

---

### 2. Reviewer Agent
- Evaluates generated content based on:
  - Age appropriateness
  - Conceptual correctness
  - Clarity
- **Output:**  
  {
    "status": "pass" or "fail",
    "feedback": ["..."]
  }

---

### 3. Refinement Loop
- If Reviewer returns **fail**:
  - Generator is re-run with feedback
- Limited to **one refinement pass**

---

## Tech Stack
- Python
- Gradio (UI)
- Ollama (local LLM)
- Groq API (optional LLM)
- python-dotenv

---

## Installation & Setup

### 1. Clone the repository or download files

### 2. Install dependencies
pip install -r requirements.txt

---

## Environment Variables

This project uses a `.env` file to securely store API keys.

### Create a `.env` file in the root directory:
GROQ_API_KEY=your_api_key_here

### Notes:
- Required only if using **Groq API**
- Do NOT share your `.env` file publicly

---

## LLM Setup

This project supports two LLM backends:



### Option 1: Groq API (Default - Faster)

1. Get API key:  
   https://console.groq.com/

2. Add to `.env`:
GROQ_API_KEY=your_api_key_here

3. By default, the app uses Groq:
USE_OLLAMA = False
---

### Option 2: Ollama (Optional - Local)

1. Install Ollama:  
   https://ollama.com/download

2. Pull the model:
ollama pull phi3

3. Run Ollama:
ollama run phi3

4. Ensure it is running at:
http://localhost:11434

3. Switch backend in code:
USE_OLLAMA = True
---

## Running the Application

python app.py

Then open:
http://127.0.0.1:7860

---

## Features
- Multi-agent architecture (Generator + Reviewer)
- Structured JSON outputs
- Feedback-driven refinement loop
- Gradio UI with visible agent workflow
- Support for local (Ollama) and API-based (Groq) LLMs

---

## Notes
- Ollama may be slower depending on system performance
- Groq provides faster and more stable responses
- Only one LLM backend is used at a time
- JSON parsing is handled to ensure structured outputs

---

## Project Structure
.
├── app.py
├── requirements.txt
├── README.md
├── .env (optional)
