import requests


def get_tools():
    validate_email_config = {
        "type": "function",
        "function": {
            "name": "validate_email",
            "description": "Validates the email address using the api inside this function. Call this whenever you need to validate the email address, for example when a customer asks 'Is this a valid email'",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Email address needs validation",
                    }
                },
                "required": ["email"]
            }
        }
    }
    tools = [validate_email_config]
    return tools


def validate_email(email):
    try:
        response = requests.get(f"https://rapid-email-verifier.fly.dev/api/validate?email={email}")
        response.raise_for_status()
        data = response.json()
        return data
        """
        if "status" in data:
            return {
                "email": email,
                "status": data["status"],
                "validations": data.get("validations", {}),
            }
        else:
            return {
                "email": email,
                "status": "UNKNOWN",
                "error": "Unexpected API response",
            }
        """
    except Exception as e:
        print(f"Error while validating email {e}")
        return {}
