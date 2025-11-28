import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.gemini_client import GeminiClient

def test_gemini_connection():
    print("Initializing GeminiClient...")
    try:
        client = GeminiClient()
        print("GeminiClient initialized successfully.")
    except ValueError as e:
        print(f"Failed to initialize GeminiClient: {e}")
        return

    print("\nTesting synchronous generation...")
    prompt = "Hello, tell me a short joke about programming."
    response = client.generate_response(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")

    # Basic validation
    if response and "Error" not in response:
        print("\nSUCCESS: Gemini API is working!")
    else:
        print("\nFAILURE: Gemini API returned an error or empty response.")

if __name__ == "__main__":
    test_gemini_connection()
