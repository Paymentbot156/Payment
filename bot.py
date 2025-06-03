
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import os

TOKEN = "7609629344:AAH-Mem-2bzv94yDyWfZGxQc5JxmRrB2xAc"
ADMIN_ID = 5670958127

GOLD_IDS = [
    "bgmi117748388", "bgmi123738384", "bgmi138949495", "bgmi148494946", "bgmi159393996",
    "bgmi168939306", "bgmi179389393", "bgmi182293939", "bgmi192939397", "bgmi192929929"
]
PLATINUM_IDS = [
    "bgmi219494040", "bgmi228393939", "bgmi239393993", "bgmi258383939", "bgmi822992393"
]
PASSWORD = "Bgmi2025@"

used_ids = {"gold": [], "platinum": []}
user_purchases = {}

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("GOLD ID 🥇 - ₹59", callback_data='gold')],
        [InlineKeyboardButton("PLATINUM ID 🥈 - ₹79", callback_data='platinum')],
        [InlineKeyboardButton("BULK BUY OPTION ❤️‍🩹", callback_data='bulk')]
    ]
    await update.message.reply_text("Choose an option:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or "NoUsername"
    context.user_data['selection'] = query.data

    if query.data == "gold" or query.data == "platinum":
        with open("qr.png", "rb") as qr:
            await query.message.reply_photo(qr, caption="Scan this QR and send payment screenshot here.")
    elif query.data == "bulk":
        keyboard = [
            [InlineKeyboardButton("5 ID GOLD - ₹245", callback_data='bulk_5_gold')],
            [InlineKeyboardButton("10 ID GOLD - ₹490", callback_data='bulk_10_gold')],
            [InlineKeyboardButton("5 ID PLATINUM - ₹345", callback_data='bulk_5_platinum')],
            [InlineKeyboardButton("10 ID PLATINUM - ₹690", callback_data='bulk_10_platinum')]
        ]
        await query.message.reply_text("Bulk Buy Options:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    selection = context.user_data.get('selection', 'unknown')
    caption = f"User @{user.username} (ID: {user.id}) has sent a payment screenshot for {selection.upper()}.
Approve?"

    keyboard = [
        [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}_{selection}"),
         InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]
    ]

    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("payment.png")

    with open("payment.png", "rb") as image:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=image, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    action, user_id = data[0], int(data[1])
    user = await context.bot.get_chat(user_id)

    if action == "approve":
        selection = data[2]
        if selection == "gold":
            available = [id for id in GOLD_IDS if id not in used_ids["gold"]]
        else:
            available = [id for id in PLATINUM_IDS if id not in used_ids["platinum"]]

        if available:
            assigned_id = available[0]
            used_ids[selection].append(assigned_id)
            msg = f"YOUR {selection.upper()} LOGIN ID 🆔 & PASSWORD BELOW 👇\n\nID- {assigned_id}\nPASS- {PASSWORD}\n\nThank you for purchasing with us!! ☺️ 1 Gold 🥇 free after 6 successfully purchase of any 🆔 🎉"

            count = user_purchases.get(user_id, 0) + 1
            user_purchases[user_id] = count

            if count == 6 and len(GOLD_IDS) > len(used_ids["gold"]):
                free_id = [id for id in GOLD_IDS if id not in used_ids["gold"]][0]
                used_ids["gold"].append(free_id)
                msg += f"\n\n🎁 FREE BONUS GOLD ID:\nID- {free_id}\nPASS- {PASSWORD}"

            await context.bot.send_message(chat_id=user_id, text=msg)
        else:
            await context.bot.send_message(chat_id=user_id, text="Sorry, all IDs are sold out.")
    elif action == "reject":
        await context.bot.send_message(chat_id=user_id, text="❌ Payment not verified. Please check again or contact @JKS6190")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button, pattern="^(gold|platinum|bulk|bulk_\d+_\w+)$"))
app.add_handler(CallbackQueryHandler(admin_response, pattern="^(approve|reject)_\d+(_\w+)?$"))
app.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))

app.run_polling()
