
import httpx

request = {
    "message": "Explain what a vector database is in simple terms.",
    "stream": False,
}

response = httpx.post(
    "http://localhost:8000/chat",
    json=request,
    timeout=60,
)

print("Status code:", response.status_code)
print("Response:", response.text)

response.raise_for_status()
