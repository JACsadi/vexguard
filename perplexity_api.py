import os
from perplexity import Perplexity

# Initialize client with explicit API key
client = Perplexity(api_key=os.environ.get("PERPLEXITY_API_KEY"))

completion = client.chat.completions.create(
    model="sonar-pro",
    messages=[
        {"role": "user", "content": "What were the results of the 2025 French Open Finals?"}
    ]
)

print(completion.choices[0].message.content)