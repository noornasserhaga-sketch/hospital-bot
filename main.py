import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# 🔥 حط التوكن هنا مؤقتًا (غيره بعدين)
TOKEN = "8531604454:AAGT7cKDaXStmXh1L2VGFq9FQLnFo6svWDY"

# 🔥 هنحط Chat ID هنا بعد ما نجيبه
ADMIN_CHAT_ID = ""

CHOOSING_CLINIC, CHOOSING_DAY, CHOOSING_TIME, GET_PHONE, GET_NAME = range(5)

# بيانات العيادات
clinics = {
    "qanater": {
        "name": "عيادة القناطر الخيرية",
        "address": "برج دريم 1 أمام مستشفى القناطر المركزى الدور الاول",
        "location": "https://maps.app.goo.gl/YLYLjwq3cd78XpBU8",
        "phones": "01276084747 - 01121863955",
        "days": {
            "السبت": ["8", "9", "10"],
            "الأربعاء": ["8", "9", "10"],
        },
    },
    "dokki": {
        "name": "عيادة الدقي",
        "address": "96 شارع التحرير فوق ايتوال الدور التالت",
        "location": "https://maps.app.goo.gl/YLYLjwq3cd78XpBU8",
        "phones": "01276084747 - 01122242087",
        "days": {
            "الأحد": ["7", "8", "9"],
            "الثلاثاء": ["6", "7", "8"],
            "الخميس": ["5", "6", "7"],
        },
    },
    "faisal": {
        "name": "عيادة فيصل",
        "address": "٣٣٩ ش حسن محمد امام بنك مصر بجوار خير زمان - الدور التانى",
        "location": "https://goo.gl/maps/fDdwoP3pxH9pjFLd8",
        "phones": "01276084747 - 01501502866",
        "days": {
            "الاثنين": ["7", "8", "9"],
            "الخميس": ["7", "8", "9"],
        },
    },
}


# 🔥 start (بيجيب Chat ID + يبدأ الحجز)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    # 👇 يجيب Chat ID
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID: {chat_id}")

    keyboard = [
        [InlineKeyboardButton("عيادة القناطر الخيرية", callback_data="qanater")],
        [InlineKeyboardButton("عيادة الدقي", callback_data="dokki")],
        [InlineKeyboardButton("عيادة فيصل", callback_data="faisal")],
    ]

    text = (
        "اهلا بحضرتك يافندم في عيادة د/ احمد حمدي حجاج\n"
        "استشارى جراحة المخ والأعصاب والعمود الفقري بكلية الطب جامعة القاهرة\n\n"
        "احجز موعد في:"
    )

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING_CLINIC


async def choose_clinic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    clinic_key = query.data
    context.user_data["clinic_key"] = clinic_key

    days = clinics[clinic_key]["days"].keys()
    keyboard = [[InlineKeyboardButton(day, callback_data=day)] for day in days]

    await query.edit_message_text(
        "اختر يوم الحجز:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_DAY


async def choose_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    day = query.data
    context.user_data["day"] = day

    clinic_key = context.user_data["clinic_key"]
    times = clinics[clinic_key]["days"][day]

    keyboard = [[InlineKeyboardButton(t, callback_data=t)] for t in times]

    await query.edit_message_text(
        "اختر الساعة:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_TIME


async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["time"] = query.data

    await query.edit_message_text("من فضلك اكتب رقم التلفون:")
    return GET_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    await update.message.reply_text("من فضلك اكتب اسم المريض:")
    return GET_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data["name"] = name

    clinic = clinics[context.user_data["clinic_key"]]
    day = context.user_data["day"]
    time = context.user_data["time"]
    phone = context.user_data["phone"]

    text = f"""
✅ تم الحجز بنجاح

👤 الاسم: {name}
📞 التليفون: {phone}

🏥 {clinic["name"]}
📅 اليوم: {day}
⏰ الساعة: {time}

📍 العنوان:
{clinic["address"]}

📌 اللوكيشن:
{clinic["location"]}

📲 للتواصل:
{clinic["phones"]}
"""

    await update.message.reply_text(text)

    # 🔥 إرسال للحجوزات للجروب
    if ADMIN_CHAT_ID:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)

    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_CLINIC: [CallbackQueryHandler(choose_clinic)],
            CHOOSING_DAY: [CallbackQueryHandler(choose_day)],
            CHOOSING_TIME: [CallbackQueryHandler(choose_time)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.run_polling()


if __name__ == "__main__":
    main()