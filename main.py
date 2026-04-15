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

# مهم:
# حطي هنا Chat ID بتاعك أو بتاع الجروب
# مؤقتًا سيبيه فاضي لحد ما نجيبه
ADMIN_CHAT_ID = ""

CHOOSING_SERVICE, CHOOSING_CLINIC, CHOOSING_DAY, CHOOSING_TIME, GET_PHONE, GET_NAME = (
    range(6)
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    keyboard = [
        [InlineKeyboardButton("حجز موعد", callback_data="book")],
        [InlineKeyboardButton("استشارة طبية", callback_data="consult")],
    ]

    text = (
        "أهلاً بك في عيادة الدكتور أحمد حمدي حجاج\n"
        "دكتور مخ وأعصاب\n\n"
        "هل تود حجز موعد أم استشارة طبية؟"
    )

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING_SERVICE


async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data

    if choice == "consult":
        await query.edit_message_text(
            "للاستشارة الطبية يرجى التواصل مع العيادة مباشرة، أو أرسل رسالتك هنا وسيتم الرد عليك لاحقًا."
        )
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("عيادة الدقي", callback_data="dokki")],
        [InlineKeyboardButton("عيادة القناطر الخيرية", callback_data="qanater")],
    ]

    await query.edit_message_text(
        "اختر العيادة:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_CLINIC


async def choose_clinic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    clinic = query.data
    context.user_data["clinic"] = (
        "عيادة الدقي" if clinic == "dokki" else "عيادة القناطر الخيرية"
    )

    if clinic == "dokki":
        keyboard = [
            [InlineKeyboardButton("الأحد", callback_data="الأحد")],
            [InlineKeyboardButton("الخميس", callback_data="الخميس")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("السبت", callback_data="السبت")],
            [InlineKeyboardButton("الأربعاء", callback_data="الأربعاء")],
        ]

    await query.edit_message_text(
        "اختر يوم الحجز:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_DAY


async def choose_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    day = query.data
    context.user_data["day"] = day

    keyboard = [
        [InlineKeyboardButton("7:00", callback_data="7:00")],
        [InlineKeyboardButton("8:00", callback_data="8:00")],
        [InlineKeyboardButton("9:00", callback_data="9:00")],
        [InlineKeyboardButton("10:00", callback_data="10:00")],
        [InlineKeyboardButton("11:00", callback_data="11:00")],
    ]

    await query.edit_message_text(
        "اختر الساعة:", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSING_TIME


async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    appointment_time = query.data
    context.user_data["time"] = appointment_time

    await query.edit_message_text("من فضلك اكتب رقم التلفون:")
    return GET_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    context.user_data["phone"] = phone

    await update.message.reply_text("من فضلك اكتب اسم المريض:")
    return GET_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    patient_name = update.message.text.strip()
    context.user_data["name"] = patient_name

    clinic = context.user_data.get("clinic", "")
    day = context.user_data.get("day", "")
    appointment_time = context.user_data.get("time", "")
    phone = context.user_data.get("phone", "")

    confirm_text = (
        "تم الحجز بنجاح ✅\n\n"
        f"اسم المريض: {patient_name}\n"
        f"رقم التلفون: {phone}\n"
        f"العيادة: {clinic}\n"
        f"اليوم: {day}\n"
        f"الساعة: {appointment_time}"
    )

    await update.message.reply_text(confirm_text)

    admin_text = (
        "حجز جديد 🏥\n\n"
        f"اسم المريض: {patient_name}\n"
        f"رقم التلفون: {phone}\n"
        f"العيادة: {clinic}\n"
        f"اليوم: {day}\n"
        f"الساعة: {appointment_time}\n"
        f"اسم الحساب: @{update.effective_user.username if update.effective_user.username else 'لا يوجد'}\n"
        f"Telegram ID: {update.effective_user.id}"
    )

    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text)
        except Exception as e:
            await update.message.reply_text(
                f"تم الحجز، لكن تعذر إرسال البيانات للإدارة: {e}"
            )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية.")
    return ConversationHandler.END


def main():
    print("TOKEN:", TOKEN)
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_SERVICE: [CallbackQueryHandler(choose_service)],
            CHOOSING_CLINIC: [CallbackQueryHandler(choose_clinic)],
            CHOOSING_DAY: [CallbackQueryHandler(choose_day)],
            CHOOSING_TIME: [CallbackQueryHandler(choose_time)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
