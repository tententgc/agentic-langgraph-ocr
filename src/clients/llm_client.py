class LLMClient:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def summarize(self, prompt: str) -> str:
        # TODO: Hook to your LLM provider
        return prompt[:5000]
