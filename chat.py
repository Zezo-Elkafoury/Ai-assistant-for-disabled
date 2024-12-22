import google.generativeai as genai
import os

# Configure the API key
API_KEY = 'AIzaSyBX6CKXmw8-6HLUaDOn4MdLuxjA0R2TElg'
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.0-flash-exp')
chat = model.start_chat(history=[])

def get_gemini_response(prompt):
    """Sends the prompt to Gemini and returns the response."""

    response = chat.send_message(prompt)
    return response.text

def main():
  print("Welcome to Gemini Chat! Type 'exit' to end the conversation.")
  while True:
    user_prompt = input("You: ")
    if user_prompt.lower() == "exit":
        break

    gemini_response = get_gemini_response(user_prompt)
    print(f"Gemini: {gemini_response}\n")

if __name__ == "__main__":
    main()
