from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class RationaleLLM:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="openai/gpt-oss-120b",
            api_key="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",
            base_url="https://openrouter.ai/api/v1",
            temperature=0
            )

        self.prompt = ChatPromptTemplate.from_template("""
You are a financial risk explanation assistant.

Rewrite the following system rationale into a clear,
professional explanation suitable for a human reviewer.

Rules:
- Do NOT introduce new facts
- Do NOT speculate
- Do NOT change meaning
- Keep it concise and neutral

System rationale:
{rationale}

Confidence score: {confidence}

Human-readable explanation:
""")

    def rewrite(self, rationale: str, confidence: float) -> str:
        response = self.llm.invoke(
            self.prompt.format(
                rationale=rationale,
                confidence=confidence
            )
        )
        return response.content.strip()