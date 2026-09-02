import json
import logging
from typing import Optional
from pydantic import BaseModel, Field

from llm.provider import BaseLLMProvider
import config

logger = logging.getLogger("promptsentinel")

class JudgeResponseSchema(BaseModel):
    decision: str = Field(description="Must be 'MALICIOUS', 'SAFE', or 'UNCERTAIN'.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")
    technique_id: Optional[str] = Field(None, description="The taxonomy ID of the technique if MALICIOUS (e.g. 'PT-001'), else null.")
    reason: str = Field(description="A short explanation of the decision.")

class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        if not config.LLM_JUDGE_API_KEY:
            raise ValueError("LLM_JUDGE_API_KEY is not set.")
        
        # Lazy initialization is requested, so we import google.genai here? 
        # "Gemini must NOT initialize during module import... The client should only be initialized when LLM_JUDGE_ENABLED=true AND Phase 17.3 determines that the prompt requires judging."
        # Actually, get_llm_provider() is only called inside evaluate_with_judge, which is only called if should_invoke_llm_judge returns True.
        # So we can import google.genai here.
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise RuntimeError("google-genai SDK is not installed.")

        # HttpOptions is accessible via types.HttpOptions
        # google-genai SDK expects timeout in milliseconds as an integer
        timeout_ms = int(float(config.LLM_JUDGE_TIMEOUT) * 1000)
        self.client = genai.Client(
            api_key=config.LLM_JUDGE_API_KEY, 
            http_options={"timeout": timeout_ms}
        )
        self.model_name = config.LLM_JUDGE_MODEL
        self.types = types

    def evaluate(self, prompt: str, context: dict) -> dict:
        system_instruction = (
            "You are an AI security judge evaluating a prompt. "
            "You will be given the original prompt and a context of tentative detections. "
            "Determine if the prompt is MALICIOUS or SAFE. "
            "Respond using the provided JSON schema."
        )

        # Build a concise context representation
        user_content = f"User Prompt: {prompt}\n\nTentative Detections Context: {json.dumps(context)}"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_content,
                config=self.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=JudgeResponseSchema,
                    temperature=0.0,
                )
            )
            
            output_text = response.text
            if not output_text:
                raise ValueError("Empty response from Gemini")
                
            data = json.loads(output_text)
            return data

        except Exception as e:
            raise Exception(f"GeminiProvider evaluation failed: {str(e)}")

