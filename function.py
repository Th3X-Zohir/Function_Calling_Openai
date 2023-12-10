import json
from openai import OpenAI
import requests

# Set your OpenAI API key
api_key = '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'

client = OpenAI(api_key=api_key)

print("OpenAI client initialized with the provided API key.")

# Define the password checking function
def check_credentials(username, password):
    print(f"Checking credentials for username: {username}")
    correct_username = "jihan"
    correct_password = "123456"
    if username == correct_username and password == correct_password:
        return "Credentials are correct."
    else:
        return "Credentials are incorrect."

# Function to run the conversation with OpenAI's Chat Completion
def run_conversation(user_input):
    print(f"Starting conversation with input: {user_input}")
    messages = [{"role": "user", "content": user_input}]

    # Define the tools (functions) available for OpenAI to use
    tools = [
        {
            "type": "function",
            "function": {
                "name": "check_credentials",
                "description": "Check if the provided username and password are correct.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "The username to check."},
                        "password": {"type": "string", "description": "The password to check."}
                    },
                    "required": ["username", "password"],
                },
            },
        }
    ]

    print("Sending request to OpenAI's Chat Completion...")
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    print("Received response from OpenAI.")
    response_message = chat_completion.choices[0].message
    
    tool_calls = response_message.tool_calls
    

    if tool_calls:
        print("Processing tool calls...")
        available_functions = {
            "check_credentials": check_credentials,
        }
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                username=function_args.get("username"),
                password=function_args.get("password"),
            )
            print(f"Function '{function_name}' called with response: {function_response}")
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        print("Sending follow-up request to OpenAI...")
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        print("Received follow-up response from OpenAI.")
        return second_response.choices[0].message
    else:
        print("No function was called.")
        return "Function was not called."

# Example usage
print("Starting example conversation...")
print(run_conversation("Can you check if my credentials are correct? My username is jihan and password is 123456"))