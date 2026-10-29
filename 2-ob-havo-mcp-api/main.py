import json
from pathlib import Path
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

app = FastAPI(title="Aqlli Ob-havo Maslahatchisi API")

# Foydalanuvchi yuboradigan so'rov qolipi
class UserQuery(BaseModel):
    query: str

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"
SERVER_FILE = Path(__file__).resolve().with_name("mcp_server.py")

async def call_llm(prompt: str, system_prompt: str, as_json: bool = False) -> str:
    """Ollama orqali LLM ga so'rov yuborish uchun universal funksiya."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    if as_json:
        payload["format"] = "json"  # LLM dan qat'iy JSON formatida javob olish

    async with httpx.AsyncClient() as client:
        res = await client.post(OLLAMA_URL, json=payload, timeout=60.0)
        return res.json()["response"]

async def mcp_ob_havo_olish(shahar: str) -> str:
    """MCP Server orqali ob-havo ma'lumotlarini tortib kelish."""
    server_params = StdioServerParameters(command="python", args=[str(SERVER_FILE)])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Biz yaratgan 'shahar_ob_havosini_olish' asbobini chaqiramiz
            result = await session.call_tool("shahar_ob_havosini_olish", {"shahar_nomi": shahar})
            for item in result.content:
                text = getattr(item, "text", None)
                if isinstance(text, str):
                    return text
            return str(result.content)

@app.post("/weather-advice")
async def ob_havo_maslahati(req: UserQuery):
    # LLM orqali shahar nomini qat'iy JSON formatida ajratib olish
    sys_extract = """
    Foydalanuvchi so'rovidan shahar nomini ingliz tilida ajratib ol.
    Faqatgina JSON qaytar: {"city": "Shahar nomi"}.
    Agar shahar nomi topilmasa: {"city": null}.
    """

    llm_json_response = await call_llm(prompt=req.query, system_prompt=sys_extract, as_json=True)

    try:
        parsed_data = json.loads(llm_json_response)
        shahar = parsed_data.get("city")
    except Exception:
        shahar = None

    if not shahar:
        return {"answer": "Kechirasiz, so'rovingizdan shahar nomini aniqlay olmadim."}

    # MCP Tool yordamida ajratib olingan shahar bo'yicha ob-havoni olish
    weather_data = await mcp_ob_havo_olish(shahar)

# Ob-havo ma'lumoti va asl savolni LLM ga berib, yakuniy chiroyli matn yasash
    sys_advice = f"""
    Sen g'amxo'r, tajribali va yordamchi ob-havo maslahatchisisan.
    Haqiqiy ob-havo ma'lumoti: {weather_data}

    Qoidalar:
    1. Til: Foydalanuvchi qaysi tilda savol bergan bo'lsa, AYNAN o'sha tilda, grammatik jihatdan to'g'ri javob qaytar (inglizcha bo'lsa inglizcha, o'zbekcha bo'lsa o'zbekcha).
    2. Maslahat: Savolga to'g'ridan-to'g'ri, qisqa va amaliy maslahat bilan javob ber (masalan, soyabon kerakligi yoki issiq kiyinish haqida).
    3. Mantiq: Faqat berilgan haqiqiy ma'lumotga tayan. Agar qor yoki yomg'ir 0.0 bo'lsa, albatta "yog'mayapti" deb ayt. To'qima ma'lumot qo'shma.

    Namunalar (shu uslubda javob ber):
    Savol: "Nyu-Yorkda qor yog'yaptimi?"
    Ma'lumot: Qor: 0.0 sm, Harorat: 16.7°C.
    Javob: "Yo'q, Nyu-Yorkda hozir qor yog'mayapti. Havo harorati 16.7°C, yupqaroq kiyinishingiz mumkin."

    Savol: "I live in London, do I need an umbrella today?"
    Ma'lumot: Harorat: 15°C, Yomg'ir: 2.5 mm.
    Javob: "Yes, you need an umbrella. It is currently raining in London and the temperature is 15°C."
    """

    yakuniy_javob = await call_llm(prompt=req.query, system_prompt=sys_advice, as_json=False)

    return {
        "query": req.query,
        "answer": yakuniy_javob.strip(),
        "extracted_city": shahar,
        "raw_weather_data": weather_data
    }