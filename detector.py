import os
import base64
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DETECTION_PROMPT = """You are an expert plant pathologist. Analyze this plant image and respond ONLY with valid JSON, no markdown, no extra text. Use exactly this structure: {"status": "healthy or diseased or warning", "disease_name": "specific disease name or Healthy Plant", "confidence": 85, "severity": "None or Mild or Moderate or Severe", "urgency": "Low or Medium or High", "description": "2-3 sentences about what you observe", "causes": ["cause 1", "cause 2", "cause 3"], "treatments": ["Step 1: action", "Step 2: action", "Step 3: action"], "prevention": ["tip 1", "tip 2", "tip 3"], "affected_parts": ["leaf", "stem"], "scientific_name": "scientific name of disease"}"""

def encode_image(image_file) -> str:
    image_file.seek(0)
    return base64.standard_b64encode(image_file.read()).decode("utf-8")

def detect_disease(image_file) -> dict:
    image_data = encode_image(image_file)
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": DETECTION_PROMPT
                    }
                ]
            }
        ],
        max_tokens=1024,
    )
    raw = response.choices[0].message.content.strip()
    clean = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(clean)

def chat_about_disease(user_question: str, diagnosis: dict, history: list) -> str:
    context = f"""You are a helpful plant disease expert. You diagnosed this plant:
Disease: {diagnosis['disease_name']}
Status: {diagnosis['status']} | Severity: {diagnosis['severity']} | Urgency: {diagnosis['urgency']}
Description: {diagnosis['description']}
Treatments: {'; '.join(diagnosis['treatments'])}
Answer questions based on this diagnosis. Be concise and practical."""

    messages = [{"role": "system", "content": context}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_question})

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=messages,
        max_tokens=512,
    )
    return response.choices[0].message.content
