import requests



def get_llm_response(system_prompt, user_prompt):
    OLLAMA_API = "http://localhost:11434/api/chat"
    HEADERS = {"Content-Type": "application/json"}
    MODEL = "llama3.2"
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format" : {"type": "json_object"},
        "stream": False
    }

    response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
    """
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
        ],
        response_format={"type": "json_object"}
    )
    """
    return response.json()['message']['content']