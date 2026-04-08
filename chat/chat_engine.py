from langchain_openai import AzureChatOpenAI
from config import AZURE
import time

# LLM Client
llm = AzureChatOpenAI(
    azure_endpoint=AZURE["endpoint"],
    api_key=AZURE["api_key"],
    api_version=AZURE["api_version"],
    azure_deployment=AZURE["chat"],
    temperature=0.8
)

# Ask LLM with Retry & Backoff
def ask_llm(prompt: str) -> str:
    """
    Sends a prompt to Azure OpenAI with automatic retry on errors.
    Prevents 429 (Rate Limit) from crashing Streamlit.
    """
    max_retries = 5          # how many times to retry
    backoff = 2              # starting backoff seconds
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt)
            return response.content

        except Exception as e:
            error_msg = str(e)

            # 429 Too Many Requests - retry
            if "429" in error_msg or "too_many_requests" in error_msg.lower():
                time.sleep(backoff)
                backoff *= 2        # exponential backoff
                continue

            # Connection / network errors - retry
            if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                time.sleep(backoff)
                backoff *= 2
                continue

            # Other errors - raise immediately
            raise e

    # If all retries fail
    raise Exception("Azure OpenAI request failed after multiple retries.")