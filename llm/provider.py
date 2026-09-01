import abc
from config import LLM_JUDGE_PROVIDER

class BaseLLMProvider(abc.ABC):
    """
    Abstract interface for LLM Judge providers.
    Providers should implement the evaluate method.
    """

    @abc.abstractmethod
    def evaluate(self, prompt: str, context: dict) -> dict:
        """
        Evaluate a prompt and detection context using an LLM.

        Args:
            prompt: The original user prompt.
            context: A dictionary containing the tentative detections to verify.

        Returns:
            A dictionary containing the parsed LLM structured output.
        """
        pass

def get_llm_provider() -> BaseLLMProvider:
    """
    Factory method to return the active LLM provider.
    """
    if LLM_JUDGE_PROVIDER == "mock":
        from llm.mock_provider import MockLLMProvider
        return MockLLMProvider()
    
    raise ValueError(f"Unknown LLM provider: {LLM_JUDGE_PROVIDER}")
