import json
from openai import OpenAI
import requests

# Set your OpenAI API key
api_key = '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'

client = OpenAI(api_key=api_key)

print("OpenAI client initialized with the provided API key.")

# Function to check credentials
def check_credentials(username, password):
    print(f"Checking credentials for username: {username}")
    correct_username = "jihan"
    correct_password = "123456"
    if username == correct_username and password == correct_password:
        return "Credentials are correct."
    else:
        return "Credentials are incorrect."

# Function to calculate the sum of two numbers
def calculate_sum(number1, number2):
    print(f"Calculating sum of {number1} and {number2}")
    return f"The sum of {number1} and {number2} is {number1 + number2}."

# Enhanced function to interact with the Node.js server
def interact_with_server(action, key, value=None):
    url = 'http://localhost:3000/'

    try:
        if action == 'store':
            response = requests.post(url + 'store', json={'key': key, 'value': value})
        elif action == 'retrieve':
            response = requests.get(url + f'retrieve/{key}')
        elif action == 'update':
            response = requests.put(url + 'update', json={'key': key, 'value': value})
        elif action == 'delete':
            response = requests.delete(url + f'delete/{key}')
        else:
            return "Invalid action"

        if response.ok:
            return response.text
        else:
            return f"Error: {response.status_code} {response.reason}"

    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

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
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_sum",
                "description": "Calculate the sum of two numbers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "number1": {"type": "number", "description": "The first number."},
                        "number2": {"type": "number", "description": "The second number."}
                    },
                    "required": ["number1", "number2"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "interact_with_server",
                "description": "Interact with a Node.js server for various actions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "The action to perform (store, retrieve, update, delete)."},
                        "key": {"type": "string", "description": "The key for the data."},
                        "value": {"type": "string", "description": "The value for the action, if needed."}
                    },
                    "required": ["action", "key"],
                    "additionalProperties": True
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
            "calculate_sum": calculate_sum,
            "interact_with_server": interact_with_server,
        }
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
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
print(run_conversation("Can you delete my data with key 'username' to  value 'jihan' in the server?"))