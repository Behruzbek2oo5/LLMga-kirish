# AI Kurs Topshiriqlari

Loyiha ikki topshiriq bo'yicha ajratilgan:

- `1-topshiriq/`: Ollama modeli, Modelfile, context window, API call va token hisoboti.
- `2-ob-havo-mcp-api/`: FastAPI ob-havo prototipi, Ollama orqali so'rovni tuzilmaga aylantirish va MCP tool.

## Talablar

- Python 3.10 yoki undan yangi versiya
- Ollama o'rnatilgan va ishga tushgan bo'lishi
- `qwen2.5:7b` modeli (`ollama pull qwen2.5:7b`)
- Ob-havo ma'lumotlarini olish uchun internet ulanishi

## Muhitni tayyorlash

Loyiha asosiy papkasida:

```bash
python -m venv .venv
source .venv/bin/activate.fish
python -m pip install -r requirements.txt
```

Windows'da virtual muhitni faollashtirish buyrug'i: `.venv\\Scripts\\activate`.

## 1-topshiriq: Ollama asoslari

`1-topshiriq/Modelfile` asosiy `qwen2.5:7b` modelidan `4096` tokenlik context oynasi va o'zbekcha system prompt bilan yangi `qwen2.5:7b-4k` modelini yaratadi. Loyiha ildiz papkasida quyidagi buyruqlarni bajaring:

```bash
ollama pull qwen2.5:7b
ollama create qwen2.5:7b-4k -f 1-topshiriq/Modelfile
ollama run qwen2.5:7b-4k
```

`ollama pull` asosiy model kompyuterda bo'lmasa yuklab oladi. `num_ctx` qiymatini `8192` yoki `16384` qilib o'zgartirsangiz, `ollama create` buyrug'ini qayta bajarib modelni yangilang. System prompt `SYSTEM` direktivasida belgilanadi. Yaratilgan model ro'yxatini `ollama list` bilan ko'rishingiz mumkin.

API misoli:

```bash
python 1-topshiriq/first_api.py
```

Ushbu misolda `first_api.py` ichidagi model nomi Ollama'da mavjud bo'lishi kerak. Fayl hozir `qwen2.5:7b` modelini so'raydi; model nomingiz boshqacha bo'lsa, shu qiymatni o'zgartiring. Javob bilan birga `prompt_eval_count` va `eval_count` chiqariladi.

## 2-topshiriq: ob-havo API va MCP

Loyiha ildizidan FastAPI serverini ishga tushiring:

```bash
uvicorn main:app --app-dir 2-ob-havo-mcp-api --reload
```

Swagger UI: <http://127.0.0.1:8000/docs>

`POST /weather-advice` endpoint'i `{"query": "I live in London, do I need an umbrella today?"}` kabi erkin matn qabul qiladi. Ollama shahar nomini ajratadi, MCP tool Open-Meteo'dan joriy ob-havoni oladi, so'ng LLM javobni tabiiy matn shaklida tuzadi.

MCP server asboblarini Ollama tool-calling misolida alohida sinash:

```bash
python 2-ob-havo-mcp-api/mcp_test.py
```

## GitHub

`.venv/`, `__pycache__/`, `.env` va yuklab olingan model fayllari repository'ga qo'shilmaydi. `requirements.txt` Python kutubxonalarini ro'yxatlaydi; Ollama modelini alohida o'rnating. API kalitlaridan foydalansangiz, ularni `.env` faylida saqlang va GitHub'ga yuklamang.