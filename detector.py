import google.generativeai as genai
import json
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

DETECTION_PROMPT = """You are an expert plant pathologist. Analyze this plant image carefully. Respond ONLY with valid JSON, no markdown, no extra text, no backticks. Use exactly this structure: {"status": "healthy or diseased or warning", "disease_name": "specific disease name or Healthy Plant", "confidence": 85, "severity": "None or Mild or Moderate or Severe", "urgency": "Low or Medium or High", "description": "2-3 sentences about what you observe", "causes": ["cause 1", "cause 2", "cause 3"], "treatments": ["Step 1: action", "Step 2: action", "Step 3: action"], "prevention": ["tip 1", "tip 2", "tip 3"], "affected_parts": ["leaf", "stem"], "scientific_name": "scientific name of disease"}"""


def detect_disease(image_file) -> dict:
    img = Image.open(image_file)
    response = model.generate_content([DETECTION_PROMPT, img])
    raw = response.text.strip()
    clean = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(clean)


def chat_about_disease(user_question: str, diagnosis: dict, history: list) -> str:
    context = f"""You are a helpful plant disease expert. You already diagnosed this plant:
Disease: {diagnosis['disease_name']}
Status: {diagnosis['status']} | Severity: {diagnosis['severity']} | Urgency: {diagnosis['urgency']}
Scientific name: {diagnosis.get('scientific_name', 'N/A')}
Description: {diagnosis['description']}
Treatments: {'; '.join(diagnosis['treatments'])}
Causes: {'; '.join(diagnosis['causes'])}
Answer the user's questions based on this diagnosis. Be concise and practical. Keep answers under 150 words."""

    chat_history = []
    for msg in history:
        chat_history.append({
            "role": msg["role"],
            "parts": [msg["content"]]
        })

    chat = model.start_chat(history=chat_history)
    response = chat.send_message(context + "\n\nUser question: " + user_question)
    return response.text