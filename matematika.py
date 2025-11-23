# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (
#     Application, CommandHandler, MessageHandler,
#     CallbackQueryHandler, ContextTypes, filters
# )
# import random, asyncio
#
# # ✅ TOKENNI kiriting
# TOKEN = "8382950499:AAFV0-K7JcY9Nw7IF_fWwwAzLgC1Y0jWZVU"
#
# # 🔢 Savol yaratish
# def new_question():
#     ops = ['+', '-', '*', '/']
#     op = random.choice(ops)
#     a, b = random.randint(1, 10), random.randint(1, 10)
#     if op == '/':
#         a = a * b  # bo‘linma butun chiqsin
#     q = f"{a} {op} {b}"
#     return q, round(eval(q), 2)
#
# # 🚀 /start komandasi
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     keyboard = [[InlineKeyboardButton("▶️ Boshlash", callback_data="start")]]
#     await update.message.reply_text(
#         "🧮 Salom! Boshlaymizmi?",
#         reply_markup=InlineKeyboardMarkup(keyboard)
#     )
#
# # 🔘 Tugmalar ishlashi
# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#
#     if query.data == "start":
#         await ask(query.message, context)
#     elif query.data == "stop":
#         await query.message.reply_text("🛑 To‘xtatildi. /start bilan qayta boshlang.")
#         context.user_data.clear()
#     elif query.data == "continue":
#         await ask(query.message, context)
#
# # ❓ Savol berish
# async def ask(msg, context):
#     q, a = new_question()
#     context.user_data["ans"] = a
#     context.user_data["wait"] = True
#
#     keyboard = [
#         [
#             InlineKeyboardButton("⏹ Stop", callback_data="stop"),
#             InlineKeyboardButton("🔁 Davom etish", callback_data="continue")
#         ]
#     ]
#     await msg.reply_text(f"❓ {q} = ?", reply_markup=InlineKeyboardMarkup(keyboard))
#
#     # 30 soniya ichida javob bo‘lmasa avtomatik to‘g‘ri javob chiqadi
#     async def timeout_check():
#         await asyncio.sleep(30)
#         if context.user_data.get("wait"):
#             context.user_data["wait"] = False
#             await msg.reply_text(f"⏰ Vaqt tugadi! ✅ To‘g‘ri javob: {a}")
#             await ask(msg, context)
#
#     asyncio.create_task(timeout_check())
#
# # ✍️ Foydalanuvchi javobi
# async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not context.user_data.get("wait"):
#         return
#
#     try:
#         user_ans = float(update.message.text)
#         correct = context.user_data["ans"]
#         context.user_data["wait"] = False
#
#         if abs(user_ans - correct) < 0.01:
#             await update.message.reply_text("🎉 To‘g‘ri! 👏 Yana bitta misol:")
#         else:
#             await update.message.reply_text(f"❌ Noto‘g‘ri! To‘g‘ri javob: {correct}")
#
#         await ask(update.message, context)
#
#     except ValueError:
#         await update.message.reply_text("Raqam kiriting 😅")
#
# # 🤖 Botni ishga tushirish
# def main():
#     app = Application.builder().token(TOKEN).build()
#
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(CallbackQueryHandler(button))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
#
#     print("🤖 Bot ishga tushdi...")
#     app.run_polling()
#
# if __name__ == "__main__":
#     main()
