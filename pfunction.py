import json
from openai import OpenAI
import requests

# Set your OpenAI API key
api_key = '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'

client = OpenAI(api_key=api_key)


# Function to interact with the Node.js server
def interact_with_server(action, key, value=None):
    url = 'http://localhost:3000/'
    print(f"\n[Server Interaction] Action: {action}, Key: {key}, Value: {value}")

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

        result = response.text
        print(f"Server Response: {result}")
        return result

    except requests.exceptions.RequestException as e:
        error_message = f"Request failed: {e}"
        print(error_message)
        return error_message

# Function to run the conversation with OpenAI's Chat Completion
def run_conversation():
    print("\n[Step 1] Sending initial user message to the model...")
    user_message = "Please perform multiple operations on the server."
    print(f"User Message: {user_message}")

    messages = [{"role": "user", "content": user_message}]
    tools = [
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

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    print("\n[Step 2] Model's response received, indicating function calls to make.")
    print(f"Model Response: {response_message.content}")

    tool_calls = response_message.tool_calls

    if tool_calls:
        print("\n[Step 3] Executing function calls in parallel...")
        available_functions = {"interact_with_server": interact_with_server}
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_response = available_functions[function_name](**function_args)
            print(f"Function Call Completed: {function_name} with response: {function_response}")
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

        print("\n[Step 4] Sending follow-up request to OpenAI with function responses...")
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
        )
        final_message = second_response.choices[0].message
        print("\n[Step 5] Received follow-up response from OpenAI.")
        print(f"Final Message from Model: {final_message.content}")
        return final_message.content
    else:
        print("\n[Step 3] No function calls were made by the model.")
        return "Function calls were not made."

# Example usage
print("\n---- Starting the Demonstration ----")
print(run_conversation())