import os
from openai import OpenAI
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Setup variables from .env
endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT").replace("/api/projects/bizbrain-agent", "/openai/v1")
deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT")
api_key = os.getenv("AZURE_AI_PROJECT_KEY")

# Initialize the client using the API Key instead of Azure Identity
client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

print(f"Testing connection to {deployment_name} using API Key...")

try:
    completion = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "user",
                "content": "Analyze this business scenario: Cappuccino sales dropped 15%. What is the first step for a reasoning agent?",
            }
        ],
    )
    print("\nModel Response:")
    print(completion.choices.message.content)
except Exception as e:
    print(f"\nAn error occurred: {e}")