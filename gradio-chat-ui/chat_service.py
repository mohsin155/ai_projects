from pydantic import validate_email
import json
from ai_tools import get_tools, validate_email
import requests
import google.generativeai as genai
from function_registry import FUNCTION_REGISTRY

def chat(message, history, model):
    #print("Received message:", message)
    print("Received history:", history)

    # Configure the API key first
    # Replace "YOUR_API_KEY" with your actual API key
    genai.configure(api_key="AIzaSyDAX14bCo6Cxd7knHf0TfM3IpF-7ulNoy4")

    # Define the system message
    system_message = "You are a helpful assistant. If the user provides one or more email addresses or asks about email validation → call the `validate_email` tool. If the message is small talk, greetings, or unrelated to email validation → respond normally, without calling any tool"

    # Define the tool
    # Note: This is a list of dictionaries, not a dictionary with a 'tools' key
    tools = [
        genai.protos.Tool(
            function_declarations=[
                genai.protos.FunctionDeclaration(
                    name="validate_email",
                    description="Validates email addresses",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "email": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Email address to validate"
                            )
                        },
                        required=["email"]
                    )
                )
            ]
        )
    ]

    # Create the model with tool support and system instruction
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=tools,
        system_instruction=system_message
    )
    messages = []
    for user_message, assistant_message in history:
        messages.append({"role": "user", "parts": [{"text": user_message}]})
        messages.append({"role": "model", "parts": [{"text": assistant_message}]})
    messages.append({"role": "user", "parts": [{"text": message}]})

    # Generate content with the model
    response = model.generate_content(messages)
    assistant_reply = ""
    if response.parts[0].function_call:
        function_name =  response.parts[0].function_call.name
        function_args = {}

        for key,value in response.parts[0].function_call.args.items():
            function_args[key] = value

        if function_name not in FUNCTION_REGISTRY:
            messages.append({"role": "model", "parts": [{"text": f"Unable to process {function_name}"}]})
            return f"Unable to process {function_name}"


        function = FUNCTION_REGISTRY[function_name]

        try:
            response = function(**function_args)
            print(f"Email validation response {response}")
            # Markdown code block for pretty JSON in chat
            assistant_reply = "```json\n" + json.dumps(response, indent=2) + "\n```"
            #return response.json()
        except Exception as e:
            assistant_reply = f"Unable to process {e}"
    else :
        assistant_reply = response.candidates[0].content.parts[0].text or ''

    messages.append({"role": "model", "parts": [{"text": assistant_reply}]})
    return assistant_reply
    # Print the response to see if the tool was called
    #print(response.candidates[0].content.parts)
    # yield "Testing"
"""
messages.append({"role": "system", "content": system_message})
for user_message, assistant_message in history:
    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": assistant_message})
messages.append({"role": "user", "content": message})

OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
MODEL = "llama3.2"
print(messages)
payload = {
    "model": MODEL,
    "messages": messages,
    "tools": get_tools(),
    "stream": False
}
print(payload)
response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
data = response.json()
print(f"Response from llm: {data}")
# Step 2: Check if the model wants to call a tool
tool_calls = data.get("message", {}).get("tool_calls", [])

if tool_calls:
    print("Model requested tool(s):", tool_calls)

    followup_messages = payload["messages"][:]
    followup_messages.append({
        "role": "assistant",
        "tool_calls": tool_calls
    })

    # Step 3: Run each tool requested
    for call in tool_calls:
        if call["name"] == "validate_email":
            args = call.get("arguments", {})
            tool_result = validate_email(**args)
            followup_messages.append({
                "role": "tool",
                "name": "validate_email",
                "content": json.dumps(tool_result)
            })

    # Step 4: Send follow-up with tool results
    followup_payload = {
        "model": "llama3.2",
        "messages": followup_messages
    }
    followup_response = requests.post(OLLAMA_API, json=followup_payload)
    return followup_response.json()["message"]["content"]
else:
    # No tools needed, return direct answer
    return data["message"]["content"]
"""
