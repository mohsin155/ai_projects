from website import Website
from llm_service import *

web = Website("https://evalueweb.com/")
print(web.links)
link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a chat bot.\n"
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""
user_prompt = f"Here is the list of links on the website of {web.url} - "
user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format.\n"
user_prompt += "Links (some might be relative links):\n"
user_prompt += "\n".join(web.links)

llm_response = get_llm_response(link_system_prompt, user_prompt)

print(llm_response)