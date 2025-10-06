import json
from typing import List, Dict, Any
from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.core.config import settings
import re

class LLMService:

    def __init__(self, api_key: str, model_name: str):
        try:
            self.client = genai.Client(api_key=api_key)
            self.model = model_name
        except Exception as e: 
            raise ValueError(f"Failed to generate AI client: {e}")
    
    def _clean_json_text(self, raw_text: str) -> str:
        """
        Cleans LLM responses by removing markdown code fences (```json ... ```).
        """
        # Remove triple backticks and optional 'json' hints
        cleaned = re.sub(r"^```(?:json)?|```$", "", raw_text.strip(), flags=re.MULTILINE)
        return cleaned.strip()

    def _generate_structure_output(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:

        try: 
            response = self.client.models.generate_content(
                model=self.model,
                contents=[user_prompt],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type='application/json'
                )
            )
            text = self._clean_json_text(response.text)
            return json.loads(text)
        except (APIError, json.JSONDecodeError, AttributeError) as e:
            print(f"Gemini API or json decode error: {e}")
            raise RuntimeError(f"Failed to get structured JSON from LLM: {e}")
    
    def generate_interview_questions(self, jd_text: str) -> List[str]:
        
        system_prompt = """
You are an expert technical interviewer. Your task is to analyze the provided 
Job Description (JD) and generate exactly 7 concise, challenging, and relevant 
interview questions. The output MUST be a JSON object with a single key 'questions' 
containing a list of the 7 generated questions.
"""
        user_prompt = f"Job Description to analyze:\n---\n{jd_text}"
        
        json_response = self._generate_structure_output(system_prompt=system_prompt, user_prompt=user_prompt)

        questions = json_response.get("questions", [])
        if not (5 <= len(questions) <= 7):
            print(f"LLM returned {len(questions)} questions. Expected 5-7")
        
        return [q.strip() for q in questions]

    def parse_resume_data(self, resume_text: str) -> Dict[str, Any]:
        
        system_prompt = """
You are a specialized HR data parser. Analyze the raw text of a resume 
and extract the candidate's core information. The output MUST be a JSON object 
with the following keys: 'name', 'email', 'phone', 'years_experience', 'top_skills', 
and 'education_summary'. Infer the best possible value for each key. 
If a piece of data is missing, use 'N/A'.
"""

        user_prompt = f"Raw Resume Text:\n---\n{resume_text}"

        return self._generate_structure_output(system_prompt, user_prompt)