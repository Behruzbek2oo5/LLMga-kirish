import os
import httpx
from mcp.server.fastmcp import FastMCP

# MCP Server
mcp = FastMCP("MeningKompyuterAsboblarim")

# Birinchi asbob (Tool): Papkadagi fayllarni ko'rish
@mcp.tool()
def papkadagi_fayllarni_korish() -> str:
    """Joriy papkada qanday fayllar borligini ro'yxat qilib qaytaradi."""
    return ", ".join(os.listdir("."))

# Ikkinchi asbob (Tool): VRAM xotirani hisoblash
@mcp.tool()
def vram_xotira_hisoblash(model_hajmi_gb: float, context_window: int) -> str:
    """Model hajmi va context window asosida taxminiy kerak bo'ladigan VRAM (GB) ni hisoblaydi."""
    kv_cache_gb = (context_window / 4096) * 0.5
    jami = round(model_hajmi_gb + kv_cache_gb, 2)
    return f"Model uchun {model_hajmi_gb} GB + Context ({context_window}) uchun {kv_cache_gb} GB = Jami {jami} GB VRAM kerak."

# Uchinchi asbob (Tool): Shahar ob-havosini olish
@mcp.tool()
def shahar_ob_havosini_olish(shahar_nomi: str) -> str:
    """Berilgan shahar nomi bo'yicha joriy ob-havo ma'lumotlarini qaytaradi."""
    try:
        # Shahar nomini koordinatalarga (latitude, longitude) o'tkazamiz
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={shahar_nomi}&count=1&language=en&format=json"
        geo_res = httpx.get(geo_url, timeout=30.0, verify=False).json()
        if not geo_res.get("results"):
            return f"Xatolik: '{shahar_nomi}' nomli shahar topilmadi."

        shahar_info = geo_res["results"][0]
        lat = shahar_info["latitude"]
        lon = shahar_info["longitude"]
        aniq_shahar = shahar_info["name"]
        mamlakat = shahar_info.get("country", "")

        # Koordinata bo'yicha real vaqtdagi ob-havoni olamiz
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,rain,snowfall,wind_speed_10m"
        w_res = httpx.get(weather_url, timeout=10.0).json()
        current = w_res.get("current", {})

        harorat = current.get("temperature_2m")
        sezilishi = current.get("apparent_temperature")
        yomgir = current.get("rain", 0)
        qor = current.get("snowfall", 0)
        shamol = current.get("wind_speed_10m")

        holat = "Ochiq/Bulutli"
        if yomgir > 0:
            holat = "Yomg'ir yog'moqda"
        elif qor > 0:
            holat = "Qor yog'moqda"

        return (
            f"Shahar: {aniq_shahar}, {mamlakat}. "
            f"Harorat: {harorat}°C (Sezilishi: {sezilishi}°C). "
            f"Holat: {holat}. "
            f"Yomg'ir: {yomgir} mm, Qor: {qor} sm, Shamol: {shamol} km/soat."
        )
    except Exception as e:
        return f"Ob-havoni olishda xatolik yuz berdi: {str(e)}"

if __name__ == "__main__":
    mcp.run()