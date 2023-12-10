
import requests

import json


import json

import openai

openai.api_key = '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'


def get_course_routine(batch, department):
    department=department.lower()
    """Get the course routine for a given batch and department from the API"""
    print("get_course_routine called with", batch, department)  # Debug statement
    api_url = f"https://routine.zohirrayhan.me/api/v1/courses?view_mode=student&batch={batch}&department={department}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10)  # Added headers and timeout
        if response.status_code == 200:
            print("API call successful")  # Debug statement
            return json.dumps(response.json())
        else:
            print("API call failed with status code:", response.status_code)  # Debug statement
            return json.dumps({"error": "Failed to fetch data"})
    except requests.exceptions.RequestException as e:
        print("API call resulted in an exception:", e)  # Debug statement
        return json.dumps({"error": "Exception occurred during API call"})


def run_conversation(user_input):
    openai.api_key = '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'

    messages = [{"role": "user", "content": user_input}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_course_routine",
                "description": "Get the course routine for a given batch and department",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "batch": {"type": "string", "description": "The batch code, e.g., 60_D"},
                        "department": {"type": "string", "description": "The department code, e.g., CSE"},
                    },
                    "required": ["batch", "department"],
                },
            },
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        available_functions = {
            "get_course_routine": get_course_routine,
        }
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                batch=function_args.get("batch"),
                department=function_args.get("department"),
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
        )
        return second_response.choices[0].message
    else:
        return "Function was not called."

# print(run_conversation())
