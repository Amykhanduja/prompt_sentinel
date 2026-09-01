from llm.provider import BaseLLMProvider

class MockLLMProvider(BaseLLMProvider):
    """
    A fake LLM provider for testing purposes.
    Can be configured to return specific outputs or raise exceptions.
    """
    def __init__(self):
        self.next_result = None
        self.next_exception = None

    def evaluate(self, prompt: str, context: dict) -> dict:
        if self.next_exception:
            raise self.next_exception
            
        if self.next_result is not None:
            return self.next_result
            
        # Default mock behavior
        return {
            "decision": "SAFE",
            "confidence": 0.95
        }
