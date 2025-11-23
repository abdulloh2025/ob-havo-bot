#!/usr/bin/env python
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ====== ENV LOAD ======
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    print("⚠️ Iltimos, .env faylga TELEGRAM_TOKEN qo‘shing.")
    exit()

# ====== API URL ======
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# ====== EMOJI FUNKSIYA ======
def weather_emoji(code):
    if code in [0, 1]:
        return "☀️"
    elif code in [2, 3]:
        return "⛅️"
    elif code in [45, 48]:
        return "🌫"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "🌧"
    elif code in [71, 73, 75, 85, 86]:
        return "❄️"
    elif code in [95, 96, 99]:
        return "⛈"
    else:
        return "🌤"

# ====== FUNKSIYALAR ======
def get_coordinates(city: str):
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    r = requests.get(GEOCODE_URL, params=params, timeout=10)
    if r.status_code != 200 or not r.json().get("results"):
        raise ValueError("City not found.")
    data = r.json()["results"][0]
    return data["latitude"], data["longitude"], data["name"]

def get_weather_data(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_min,temperature_2m_max,weathercode",
        "current_weather": True,
        "timezone": "auto",
    }
    r = requests.get(FORECAST_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

# ====== KO‘P TILLI SO‘ZLAR ======
LANG = {
    "uz": {
        "choose_lang": "🌐 Tilni tanlang:",
        "menu": "🇺🇿 O‘zbekiston yoki 🌍 Boshqa davlatlardan birini tanlang:",
        "uz_regions": "🇺🇿 Qaysi viloyatni tanlaysiz?",
        "world_countries": "🌍 Qaysi davlatni tanlaysiz?",
        "again": "🔁 Yana qaysi joyni ob-havosini ko‘rmoqchisiz?",
        "source": "Manba: Open-Meteo (open-meteo.com)",
        "clothing": {
            "cold": "🧥 Havo sovuq, issiq kiyim kiying!",
            "mild": "🧶 Engil kiyim kiying, havo mo‘tadil ☁️",
            "warm": "👕 Havo iliq, yengil kiyim kifoya 🌞"
        }
    },
    "ru": {
        "choose_lang": "🌐 Выберите язык:",
        "menu": "🇺🇿 Узбекистан или 🌍 Другие страны:",
        "uz_regions": "🇺🇿 Выберите область:",
        "world_countries": "🌍 Выберите страну:",
        "again": "🔁 Хотите посмотреть другой город?",
        "source": "Источник: Open-Meteo",
        "clothing": {
            "cold": "🧥 На улице холодно, одевайтесь тепло!",
            "mild": "🧶 Умеренная погода, наденьте легкую одежду ☁️",
            "warm": "👕 Тепло, достаточно легкой одежды 🌞"
        }
    },
    "en": {
        "choose_lang": "🌐 Choose your language:",
        "menu": "🇺🇿 Uzbekistan or 🌍 Other countries:",
        "uz_regions": "🇺🇿 Select a region:",
        "world_countries": "🌍 Select a country:",
        "again": "🔁 Would you like to check another location?",
        "source": "Source: Open-Meteo (open-meteo.com)",
        "clothing": {
            "cold": "🧥 It's cold outside, wear warm clothes!",
            "mild": "🧶 Mild weather, wear light clothes ☁️",
            "warm": "👕 Warm day, light clothes are enough 🌞"
        }
    },
}

# ====== MA’LUMOTLAR ======
REGIONS = [
    "Toshkent", "Samarqand", "Buxoro", "Namangan",
    "Farg‘ona", "Andijon", "Navoiy", "Jizzax",
    "Sirdaryo", "Qashqadaryo", "Surxondaryo", "Xorazm"
]

COUNTRIES = [
    "Dubai", "Moscow", "New York", "London", "Paris",
    "Tokyo", "Delhi", "Berlin", "Istanbul", "Seoul", "Rome", "Beijing"
]

# ====== FORMAT FUNKSIYA ======
def format_weather(city, data, lang="uz"):
    current = data["current_weather"]
    daily = data["daily"]

    temp = current["temperature"]
    if temp <= 10:
        clothing_text = LANG[lang]["clothing"]["cold"]
    elif 10 < temp < 20:
        clothing_text = LANG[lang]["clothing"]["mild"]
    else:
        clothing_text = LANG[lang]["clothing"]["warm"]

    text = [f"📍 <b>{city}</b>\n"]
    text.append(f"{weather_emoji(current['weathercode'])} <b>{temp}°C</b>\n")
    text.append(clothing_text + "\n")

    for i in range(3):
        date = datetime.fromisoformat(daily["time"][i]).strftime("%d-%m")
        text.append(
            f"{weather_emoji(daily['weathercode'][i])} {date} — "
            f"min: {daily['temperature_2m_min'][i]:.1f}°, "
            f"max: {daily['temperature_2m_max'][i]:.1f}°"
        )

    text.append(f"\n✅ {LANG[lang]['source']}")
    return "\n".join(text)

# ====== HANDLERLAR ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]
    await update.message.reply_text("🌐 Tilni tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Til tanlandi
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        keyboard = [
            [
                InlineKeyboardButton("🇺🇿 O‘zbekiston", callback_data="uz_regions"),
                InlineKeyboardButton("🌍 Boshqa davlatlar", callback_data="world_countries"),
            ]
        ]
        await query.edit_message_text(LANG[lang]["menu"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Viloyatlar
    if data == "uz_regions":
        lang = context.user_data.get("lang", "uz")
        keyboard = [
            [InlineKeyboardButton(region, callback_data=region)] for region in REGIONS
        ]
        await query.edit_message_text(LANG[lang]["uz_regions"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Davlatlar
    if data == "world_countries":
        lang = context.user_data.get("lang", "uz")
        keyboard = [
            [InlineKeyboardButton(country, callback_data=country)] for country in COUNTRIES
        ]
        await query.edit_message_text(LANG[lang]["world_countries"], reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Joy tanlandi
    if data in REGIONS + COUNTRIES:
        lang = context.user_data.get("lang", "uz")
        await query.edit_message_text(f"🔎 {data} uchun ob-havo olinmoqda...")
        try:
            lat, lon, city_name = get_coordinates(data)
            weather_data = get_weather_data(lat, lon)
            msg = format_weather(city_name, weather_data, lang)

            # Natijadan keyin menyu qaytadi
            keyboard = [
                [
                    InlineKeyboardButton("🇺🇿 O‘zbekiston", callback_data="uz_regions"),
                    InlineKeyboardButton("🌍 Boshqa davlatlar", callback_data="world_countries"),
                ]
            ]
            await query.edit_message_text(
                msg + f"\n\n{LANG[lang]['again']}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Xato: {e}")

# ====== MAIN ======
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
