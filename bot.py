import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import os
from io import BytesIO

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = "7609629344:AAH-Mem-2bzv94yDyWfZGxQc5JxmRrB2xAc"
ADMIN_ID = 5670958127

# ID Stocks
GOLD_IDS = [
    f"bgmi11774{i}" for i in range(8388, 8428)
]
PLATINUM_IDS = [
    f"bgmi21949{i}" for i in range(4040, 4070)
]

# Track usage
used_gold = []
used_plat = []

# Start command
def start(update: Update, context: CallbackContext):
    buttons = [[
        InlineKeyboardButton("GOLD ID 🥇 - ₹59", callback_data='gold'),
        InlineKeyboardButton("PLATINUM ID 🥈 - ₹79", callback_data='plat')
    ], [
        InlineKeyboardButton("BULK BUY OPTION ❤︸️", callback_data='bulk')
    ]]
    update.message.reply_text("Choose your plan:", reply_markup=InlineKeyboardMarkup(buttons))

# Handle random text
def handle_text(update: Update, context: CallbackContext):
    start(update, context)

# Button clicks
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'gold':
        send_qr(query, 'GOLD', 59)
    elif query.data == 'plat':
        send_qr(query, 'PLATINUM', 79)
    elif query.data == 'bulk':
        bulk_buttons = [[
            InlineKeyboardButton("5 ID GOLD - ₹245", callback_data='bulk_5_gold'),
            InlineKeyboardButton("10 ID GOLD - ₹490", callback_data='bulk_10_gold')
        ], [
            InlineKeyboardButton("5 ID PLATINUM - ₹345", callback_data='bulk_5_plat'),
            InlineKeyboardButton("10 ID PLATINUM - ₹690", callback_data='bulk_10_plat')
        ]]
        query.edit_message_text("Choose bulk option:", reply_markup=InlineKeyboardMarkup(bulk_buttons))
    else:
        plan_map = {
            'bulk_5_gold': ('GOLD', 245, 5),
            'bulk_10_gold': ('GOLD', 490, 10),
            'bulk_5_plat': ('PLATINUM', 345, 5),
            'bulk_10_plat': ('PLATINUM', 690, 10)
        }
        plan, price, count = plan_map[query.data]
        send_qr(query, plan, price, count)

# Send QR
def send_qr(query, plan, amount, count=1):
    context = query.message.bot
    context.send_photo(chat_id=query.from_user.id, photo=open("phonepeQR.jpg", 'rb'),
                       caption=f"Send ₹{amount} via QR and send screenshot here\n\nPlan: {plan} × {count}")
    context_data[query.from_user.id] = (plan, count)

# Handle screenshot
context_data = {}

def handle_photo(update: Update, context: CallbackContext):
    user = update.message.from_user
    if user.id not in context_data:
        update.message.reply_text("Please select a plan first using /start")
        return

    plan, count = context_data[user.id]
    caption = f"Payment screenshot\nUser: {user.username} ({user.id})\nPlan: {plan} × {count}"
    buttons = [
        [InlineKeyboardButton("Approve", callback_data=f"approve|{user.id}|{plan}|{count}"),
         InlineKeyboardButton("Reject", callback_data=f"reject|{user.id}")]
    ]
    photo_file = update.message.photo[-1].get_file()
    photo_bytes = BytesIO(photo_file.download_as_bytearray())
    context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_bytes, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    update.message.reply_text("Sent for admin approval. Please wait.")

# Admin decision
def admin_action(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split('|')

    if data[0] == 'approve':
        user_id, plan, count = int(data[1]), data[2], int(data[3])
        ids = []
        if plan == 'GOLD':
            ids = [id for id in GOLD_IDS if id not in used_gold][:count]
            used_gold.extend(ids)
        else:
            ids = [id for id in PLATINUM_IDS if id not in used_plat][:count]
            used_plat.extend(ids)

        msg = ""
        for id in ids:
            msg += f"\n\nYOUR {plan} LOGIN ID 🆔 & PASSWORD BELOW 👇\n\nID- {id}\nPASS- Bgmi2025@\n\nIf you find any issue contact - @JKS6190 ✅\n\nThank you for purchasing with us!! ☺️ 1 Gold 🥇 free after 6 successful purchases of any 🆔 🎉"

        context.bot.send_message(chat_id=user_id, text=msg)
        query.edit_message_caption(caption="Approved ✅")

    elif data[0] == 'reject':
        user_id = int(data[1])
        context.bot.send_message(chat_id=user_id, text="Payment not verified. Please check or contact @JKS6190")
        query.edit_message_caption(caption="Rejected ❌")

# Main
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(CallbackQueryHandler(button_handler, pattern='^(gold|plat|bulk|bulk_.*)$'))
app.add_handler(CallbackQueryHandler(admin_action, pattern='^(approve|reject)'))

app.run_polling()
