import requests

resp = requests.get(
    "https://paperswithcode.com/api/v1/papers/",
    params={"q": "diffusion models", "items_per_page": 5},
    timeout=15,
)
print("Status:", resp.status_code)
print("Content-Type:", resp.headers.get("content-type"))
print("Body (first 500 chars):")
print(resp.text[:500])