import google.generativeai as genai
import os

# 1. Setup
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. Use the model that worked for you
model = genai.GenerativeModel("gemini-2.5-flash")

# 3. Start a chat session (starts with empty history)
chat_session = model.start_chat(history=[])

print("--- Chat Started (Type 'quit' to exit) ---")

while True:
    # Get input from you in the terminal
    user_input = input("You: ")

    # Allow a way to exit the loop
    if user_input.lower() in ["quit", "exit"]:
        break

    try:
        # Send message to the active chat session
        # stream=True makes the text appear as it is being generated (faster feel)
        response = chat_session.send_message(user_input, stream=True)

        print("Gemini: ", end="")
        for chunk in response:
            print(chunk.text, end="")
        print("\n")  # New line after response

    except Exception as e:
        print(f"Error: {e}")