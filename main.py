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

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = -1003948007176

CHOOSING_CLINIC, CHOOSING_DAY, CHOOSING_TIME, GET_PHONE, GET_NAME, GET_AGE = range(6)

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


def is_valid_egyptian_phone(phone: str) -> bool:
    phone = phone.strip()
    return phone.isdigit() and len(phone) == 11 and phone.startswith("01")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["started"] = True

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


async def start_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # يبدأ الحجز من أي رسالة عادية لو المستخدم مش داخل حوار بالفعل
    if context.user_data.get("started"):
        return

    return await start(update, context)


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
    phone = update.message.text.strip()

    if not is_valid_egyptian_phone(phone):
        await update.message.reply_text(
            "رقم الموبايل غير صحيح.\n"
            "من فضلك اكتب رقم موبايل صحيح يبدأ بـ 01 ويكون 11 رقم."
        )
        return GET_PHONE

    context.user_data["phone"] = phone
    await update.message.reply_text("من فضلك اكتب اسم المريض:")
    return GET_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    context.user_data["name"] = name

    await update.message.reply_text("من فضلك اكتب السن:")
    return GET_AGE


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = update.message.text.strip()

    if not age.isdigit():
        await update.message.reply_text("من فضلك اكتب السن بشكل صحيح بالأرقام فقط.")
        return GET_AGE

    context.user_data["age"] = age

    clinic = clinics[context.user_data["clinic_key"]]
    day = context.user_data["day"]
    time = context.user_data["time"]
    phone = context.user_data["phone"]
    name = context.user_data["name"]

    user_text = f"""
✅ تم الحجز بنجاح

👤 الاسم: {name}
🎂 السن: {age}
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

    group_text = f"""
🚨 حجز جديد

👤 الاسم: {name}
🎂 السن: {age}
📞 التليفون: {phone}

🏥 العيادة: {clinic["name"]}
📅 اليوم: {day}
⏰ الساعة: {time}

📍 العنوان:
{clinic["address"]}

📌 اللوكيشن:
{clinic["location"]}

📲 أرقام العيادة:
{clinic["phones"]}

🆔 Telegram User ID: {update.effective_user.id}
"""

    await update.message.reply_text(user_text)

    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=group_text)
    except Exception:
        await update.message.reply_text("تم الحجز، لكن تعذر إرسال البيانات إلى الجروب.")

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("تم إلغاء العملية. ابعت أي رسالة للبدء من جديد.")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, start_from_text),
        ],
        states={
            CHOOSING_CLINIC: [CallbackQueryHandler(choose_clinic)],
            CHOOSING_DAY: [CallbackQueryHandler(choose_day)],
            CHOOSING_TIME: [CallbackQueryHandler(choose_time)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    app.add_handler(conv)
    app.run_polling()


if __name__ == "__main__":
    main()
