import json
import requests
import gradio as gr
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

def extract_json(text):
    try:
        return json.loads(text)
    except:
        import re

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except Exception as e:
                print(" Broken JSON:", json_str)
                raise e

        raise Exception(" No JSON found in response")
    
def validate_output(data):
    try:
        if "explanation" not in data or "mcqs" not in data:
            return False

        for q in data["mcqs"]:
            if len(q["options"]) != 4:
                return False
            if q["answer"] not in q["options"] and q["answer"] not in ["A", "B", "C", "D"]:
                return False

        return True
    except:
        return False

# config

USE_OLLAMA = False   # set True if you want to use local ollama
OLLAMA_MODEL = "phi3"  # or llama3, mistral, etc.

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"


# LLM callers

def call_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=payload)
    data = response.json()

    print("OLLAMA RAW:", data)

    if "response" in data:
        return data["response"]
    elif "error" in data:
        raise Exception(f"Ollama error: {data['error']}")
    else:
        raise Exception(f"Unexpected Ollama response: {data}")


def call_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    response = requests.post(url, headers=headers, json=payload)

    data = response.json()

    print("Groq response:", data)

    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Groq API error: {data}")

def call_llm(prompt):
    if USE_OLLAMA:
        return call_ollama(prompt)
    else:
        return call_groq(prompt)


# Generator agent

def generator_agent(grade, topic, feedback=None):
    feedback_text = ""
    if feedback:
        feedback_text = f"\nImprove based on this feedback:\n{feedback}\n"

    prompt = f"""
You are a teaching assistant.

Generate educational content for:
Grade: {grade}
Topic: {topic}

Rules:
- Use simple language appropriate for the grade
- Explanation should be short and clear
- Create exactly 3 MCQs
- Each MCQ must have 4 options
- Provide correct answer

{feedback_text}

STRICT RULE:
Return ONLY valid JSON.
Do NOT include any explanation or text outside JSON.
Ensure JSON is perfectly valid.

Each MCQ must strictly follow:
- 4 separate options (no combined string)
- Answer must match one of the options exactly

Format:
{{
  "explanation": "...",
  "mcqs": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "A"
    }}
  ]
}}
"""

    response = call_llm(prompt)

    print("\n GENERATOR RAW OUTPUT:\n", response)

    return extract_json(response)


# Reviewer agent

def reviewer_agent(content_json, grade):
    prompt = f"""
You are a strict reviewer.

Evaluate this educational content for Grade {grade}.

Check:
- Age appropriateness
- Concept correctness
- Clarity

Content:
{json.dumps(content_json, indent=2)}

STRICT RULE:
Return ONLY valid JSON.
No extra text.
No explanation outside JSON.

Format:
{{
  "status": "pass" or "fail",
  "feedback": ["..."]
}}
"""

    response = call_llm(prompt)

    print("\n REVIEWER RAW OUTPUT:\n", response)

    return extract_json(response)


# Pipeline

def run_pipeline(grade, topic):
    logs = []

    # Step 1: Generator
    logs.append(" Running Generator Agent...")
    gen_output = generator_agent(grade, topic)

    if not validate_output(gen_output):
        raise Exception(" Invalid Generator Output Format")

    # Step 2: Reviewer
    logs.append("🔍 Running Reviewer Agent...")
    review = reviewer_agent(gen_output, grade)

    refined_output = None

    # Step 3: Refinement (if needed)
    if review["status"] == "fail":
        logs.append(" Reviewer failed. Refining content...")
        refined_output = generator_agent(
            grade,
            topic,
            feedback="\n".join(review["feedback"])
        )
    else:
        logs.append(" Content passed review.")

    return (
        "\n".join(logs),
        json.dumps(gen_output, indent=2),
        json.dumps(review, indent=2),
        json.dumps(refined_output, indent=2) if refined_output else "No refinement needed"
    )


# UI (Gradio)

with gr.Blocks() as app:
    gr.Markdown("# 🤖 AI Agent Pipeline (Generator + Reviewer)")

    with gr.Row():
        grade = gr.Dropdown([1,2,3,4,5,6], label="Select Grade", value=4)
        topic = gr.Textbox(label="Enter Topic", placeholder="e.g., Types of angles")

    run_btn = gr.Button("Run Agents")

    gr.Markdown("## ⚙️ Agent Flow Logs")
    logs_output = gr.Textbox(lines=6)

    gr.Markdown("## 📘 Generator Output")
    gen_output = gr.Code(language="json")

    gr.Markdown("## 🔍 Reviewer Output")
    review_output = gr.Code(language="json")

    gr.Markdown("## 🔁 Refined Output")
    refined_output = gr.Code(language="json")

    run_btn.click(
        fn=run_pipeline,
        inputs=[grade, topic],
        outputs=[logs_output, gen_output, review_output, refined_output]
    )


app.launch()