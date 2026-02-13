import os
import dateparser
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)

# ===== TOKEN =====
TOKEN = os.getenv("TOKEN")

# ===== START =====
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🤖 Bot nhắc việc đã online!\n\n"
        "Bạn có thể nói tự nhiên, ví dụ:\n"
        "👉 nhắc tôi 10 phút nữa kiểm tra đơn\n"
        "👉 nhắc tôi 8h tối mai đóng hàng\n\n"
        "Hoặc dùng lệnh:\n"
        "/remindat YYYY-MM-DD HH:MM nội dung"
    )

# ===== CALLBACK NHẮC =====
def remind_callback(context: CallbackContext):
    job = context.job
    context.bot.send_message(
        job.context["chat_id"],
        f"⏰ NHẮC VIỆC:\n{job.context['text']}"
    )

# ===== LỆNH CŨ remindat =====
def remind_at(update: Update, context: CallbackContext):
    try:
        if len(context.args) < 3:
            update.message.reply_text(
                "❌ Dùng:\n/remindat YYYY-MM-DD HH:MM nội dung"
            )
            return

        date_str = context.args[0]
        time_str = context.args[1]
        text = " ".join(context.args[2:])

        target_time = datetime.strptime(
            f"{date_str} {time_str}",
            "%Y-%m-%d %H:%M"
        )

        now = datetime.now()

        if target_time <= now:
            update.message.reply_text("❌ Thời gian phải ở tương lai.")
            return

        delay = (target_time - now).total_seconds()

        context.job_queue.run_once(
            remind_callback,
            when=delay,
            context={
                "chat_id": update.message.chat_id,
                "text": text
            }
        )

        update.message.reply_text(
            f"✅ Đã đặt lịch lúc {time_str} ngày {date_str}"
        )

    except Exception:
        update.message.reply_text("❌ Sai định dạng thời gian.")

# ===== AI HIỂU TIẾNG VIỆT =====
def smart_remind(update: Update, context: CallbackContext):
    text = update.message.text.lower()

    # chỉ xử lý khi có chữ nhắc
    if "nhắc" not in text:
        return

    # parse thời gian tiếng Việt
    dt = dateparser.parse(
        text,
        languages=["vi"],
        settings={"PREFER_DATES_FROM": "future"}
    )

    if not dt:
        update.message.reply_text("❌ Tôi chưa hiểu thời gian bạn nói 😢")
        return

    delay = (dt - datetime.now()).total_seconds()

    if delay <= 0:
        update.message.reply_text("❌ Thời gian phải ở tương lai.")
        return

    context.job_queue.run_once(
        remind_callback,
        when=delay,
        context={
            "chat_id": update.message.chat_id,
            "text": text
        }
    )

    update.message.reply_text(
        f"🧠 OK hiểu rồi!\n⏰ Tôi sẽ nhắc bạn lúc {dt.strftime('%H:%M %d-%m-%Y')}"
    )

# ===== MAIN =====
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("remindat", remind_at))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, smart_remind))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
