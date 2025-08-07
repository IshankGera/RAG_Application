import requests
import json

# URL of the FastAPI backend
API_URL = "http://127.0.0.1:8000/ask"

def ask_consultant(question: str):
    """
    Sends a question to the AI consultant API and prints the response.
    """
    payload = {"question": question}
    headers = {"Content-Type": "application/json"}

    print(f"[*] Asking question: {question}\n")

    try:
        response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()

        print("="*50)
        print(f"Answer: {data.get('answer')}")
        print("-"*50)
        print(f"Status: {data.get('status')}")
        print("-"*50)
        print("Source Text Used:")
        print(data.get('source'))
        print("="*50)

    except requests.exceptions.RequestException as e:
        print(f"[!] Error connecting to the API: {e}")
    except json.JSONDecodeError:
        print("[!] Error: Failed to decode JSON from response.")
        print(f"    Response text: {response.text}")


if __name__ == "__main__":
    #Modify the questions as per your documents.
    # --- Test Case 1: Question that can be answered from context ---
    question_1 = ""
    ask_consultant(question_1)

    print("\n\n")

    # --- Test Case 2: Another question that can be answered ---
    question_2 = ""
    ask_consultant(question_2)
    
    print("\n\n")

    # --- Test Case 3: Question that CANNOT be answered from context ---
    question_3 = ""
    ask_consultant(question_3)