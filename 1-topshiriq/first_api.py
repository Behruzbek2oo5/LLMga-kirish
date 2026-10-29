import httpx

# Ollama ning kompyuterimizdagi API manzili
url = "http://localhost:11434/api/generate"

# Modelga yuboriladigan ma'lumot (JSON formatida)
payload = {
    "model": "gemma3-8k",
    "prompt": "FastAPI nima?",
    "stream": False  # Javobni bo'lib-bo'lib emas, bittada to'liq olish uchun
}

# API Call (So'rov yuborish)
response = httpx.post(url, json=payload, timeout=30.0)
data = response.json()

print("=== MODEL JAVOBI ===")
print(data["response"])

print("\n=== TOKENLAR HISOBOTI ===")
print(f"Input tokenlar (prompt_eval_count): {data['prompt_eval_count']}")
print(f"Output tokenlar (eval_count): {data['eval_count']}")
print(f"Jami sarflangan tokenlar: {data['prompt_eval_count'] + data['eval_count']}")
