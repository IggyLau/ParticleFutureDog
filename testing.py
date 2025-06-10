import openai
import os

# Use your environment variable (set as discussed above)
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    print("OPENAI_API_KEY not found in environment variables!")
    exit(1)

# Instantiate the OpenAI client (v1.x and above)
client = openai.OpenAI(api_key=api_key)

prompt_text = input("Enter your prompt: ")

try:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # You can use "gpt-4" or "gpt-4o" if you have access
        messages=[{"role": "user", "content": prompt_text}],
        max_tokens=100
    )
    print("Response:\n", response.choices[0].message.content)
except Exception as e:
    print("Error:", e)