#!/usr/bin/env python3
import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ====== ENV LOAD ======
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWM_KEY = os.getenv("OPENWEATHER_API_KEY")

if not BOT_TOKEN or not OWM_KEY:
    raise SystemExit("⚠️ Iltimos, .env faylga TELEGRAM_TOKEN va OPENWEATHER_API_KEY qo‘shing.")

# ====== API URL ======
GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_HOURLY_URL = "https://pro.openweathermap.org/data/2.5/forecast/hourly"

# ====== FUNKSIYALAR ======

def get_coordinates(city: str):
    """Shahar nomidan lat/lon olish"""
    params = {"q": city, "limit": 1, "appid": OWM_KEY}
    r = requests.get(GEOCODE_URL, params=params, timeout=10)
    if r.status_code != 200 or not r.json():
        raise ValueError("Shahar topilmadi.")
    data = r.json()[0]
    return data["lat"], data["lon"], data["name"]

def get_current_weather(lat, lon):
    params = {"lat": lat, "lon": lon, "appid": OWM_KEY, "units": "metric", "lang": "uz"}
    r = requests.get(CURRENT_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def get_hourly_forecast(lat, lon):
    params = {"lat": lat, "lon": lon, "appid": OWM_KEY, "units": "metric", "lang": "uz"}
    r = requests.get(FORECAST_HOURLY_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def summarize_daily(hourly_data, tz_offset, target_date):
    """Berilgan sana uchun min, max, o‘rtacha harorat va ob-havo matni"""
    temps = []
    desc = []
    for item in hourly_data.get("list", []):
        local_dt = datetime.fromtimestamp(item["dt"], timezone.utc) + timedelta(seconds=tz_offset)
        if local_dt.date() == target_date:
            temps.append(item["main"]["temp"])
            desc.append(item["weather"][0]["description"])
    if not temps:
        return None
    from collections import Counter
    return {
        "min": min(temps),
        "max": max(temps),
        "avg": sum(temps) / len(temps),
        "desc": Counter(desc).most_common(1)[0][0]
    }

def format_weather(city, current, today, tomorrow):
    text = [f"📍 <b>{city}</b>\n"]
    text.append(f"🌡️ Hozir: {current['main']['temp']:.1f}°C, {current['weather'][0]['description']}")
    text.append(f"💧 Namlik: {current['main']['humidity']}%\n")

    if today:
        text.append(f"📅 <b>Bugun</b>: o‘rtacha {today['avg']:.1f}°C (min {today['min']:.1f}°, max {today['max']:.1f}°)")
        text.append(f"  ☁️ {today['desc']}\n")
    if tomorrow:
        text.append(f"📅 <b>Ertaga</b>: o‘rtacha {tomorrow['avg']:.1f}°C (min {tomorrow['min']:.1f}°, max {tomorrow['max']:.1f}°)")
        text.append(f"  ☁️ {tomorrow['desc']}\n")

    text.append("\n✅ Manba: OpenWeather PRO API")
    return "\n".join(text)

# ====== HANDLERLAR ======

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 👋 Men OpenWeather PRO API asosida ishlaydigan ob-havo botman.\n\n"
        "Shunchaki shahar nomini yuboring — masalan: <b>Tashkent</b> yoki /weather Tashkent",
        parse_mode="HTML"
    )

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        city = " ".join(context.args)
    else:
        await update.message.reply_text("Iltimos, shahar nomini kiriting. Misol: /weather Samarkand")
        return
    await send_weather(update, city)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    await send_weather(update, city)

async def send_weather(update: Update, city):
    try:
        lat, lon, city_name = get_coordinates(city)
        current = get_current_weather(lat, lon)
        forecast = get_hourly_forecast(lat, lon)
        tz_offset = current.get("timezone", 0)

        today = (datetime.now(timezone.utc) + timedelta(seconds=tz_offset)).date()
        tomorrow = today + timedelta(days=1)

        today_summary = summarize_daily(forecast, tz_offset, today)
        tomorrow_summary = summarize_daily(forecast, tz_offset, tomorrow)

        msg = format_weather(city_name, current, today_summary, tomorrow_summary)
        await update.message.reply_html(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

# ====== MAIN ======

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
