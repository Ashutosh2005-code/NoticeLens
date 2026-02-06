import requests
import json

def query(question):
    print(f"Asking: {question}")
    try:
        resp = requests.post("http://127.0.0.1:8000/query", json={"question": question})
        if resp.status_code == 200:
            data = resp.json()
            print("Answer:", data.get("answer", "No answer found"))
            print("Sources:", data.get("sources", []))
        else:
            print(f"Error: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("--- Verifying 'giet' removal ---")
    query("Tell me about GIET")
    print("\n--- Verifying 'example.com' ---")
    query("What is this website domain or example?")
