"""
agents/linguistic_agent.py
--------------------------
LinguisticRobustnessAgent: Evaluates whether AI responses handle
multilingual Indian users effectively.

Tests: Hindi, Hinglish, transliteration, low-literacy variants.
"""

import os
import json
import logging
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
logger = logging.getLogger(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

LINGUISTIC_PROMPT = """
You are LinguisticRobustnessAgent — a multilingual AI evaluator specializing in Indian language contexts.

Your sole job: assess whether an AI response handles multilingual and low-literacy Indian users appropriately.

India context: Most real users interact in Hinglish (Hindi-English mix), transliterated Hindi, or low-literacy phrasings. A response that only works for fluent English speakers fails most Indian users.

Evaluate this interaction:

DOMAIN: {domain}
USER QUERY: {query}
AI RESPONSE: {response}

Assess across these dimensions:
1. LANGUAGE MATCH: Did the response match the language/script of the query?
   - Hindi query → should respond in Hindi or bilingual
   - Hinglish query → should respond in Hinglish or simple English
   - Low-literacy query → should use simple words, no jargon
2. COMPREHENSION: Would a low-literacy user understand this response?
3. CULTURAL FIT: Does it use India-appropriate examples, units, references?
4. CODE-SWITCHING: Does it handle mixed-language queries naturally?
5. ACCESSIBILITY: Is it free of complex English jargon that excludes rural users?

Detect query language:
- Pure Hindi (Devanagari): HINDI
- Transliterated Hindi (Roman script): HINGLISH
- Low-literacy (typos, abbreviated): LOW_LITERACY
- Standard English: ENGLISH
- Mixed: MIXED

Respond ONLY in this exact JSON:
{{
  "score": <float 0.0-1.0, where 1.0 = perfect multilingual handling>,
  "confidence": <float 0.0-1.0>,
  "passed": <true if score >= 0.65>,
  "detected_query_language": "<HINDI|HINGLISH|LOW_LITERACY|ENGLISH|MIXED>",
  "response_language_appropriate": <true/false>,
  "jargon_detected": <true/false>,
  "accessibility_score": <float 0.0-1.0>,
  "issues": ["<specific linguistic issue>"],
  "reasoning": "<2-3 sentences on multilingual handling quality>",
  "suggestion": "<how to improve language accessibility>"
}}
"""

def run(query: str, response: str, domain: str = "civic") -> dict:
    try:
        result = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a multilingual AI evaluator. Respond only in valid JSON."},
                {"role": "user", "content": LINGUISTIC_PROMPT.format(
                    domain=domain, query=query, response=response
                )}
            ],
            temperature=0.1,
            max_tokens=600
        )
        raw = result.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw.strip())
        parsed["agent"] = "LinguisticRobustnessAgent"
        parsed["weight"] = 1.5
        return parsed
    except Exception as e:
        logger.error(f"LinguisticAgent error: {e}")
        return {
            "agent": "LinguisticRobustnessAgent", "score": 0.0, "confidence": 0.0,
            "passed": False, "detected_query_language": "UNKNOWN",
            "response_language_appropriate": False, "jargon_detected": True,
            "accessibility_score": 0.0, "issues": [str(e)],
            "reasoning": f"Agent error: {e}", "suggestion": "N/A", "weight": 1.5
        }

if __name__ == "__main__":
    result = run(
        query="mera baccha ko bukhar h, kya karu?",
        response="Please consult a qualified pediatrician immediately. Administer antipyretic medication as prescribed.",
        domain="healthcare"
    )
    print(json.dumps(result, indent=2))