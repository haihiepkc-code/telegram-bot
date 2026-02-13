import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import datetime

TOKEN = os.getenv("TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Bot đang online 24/7!")

def remind_callback(context: CallbackContext):
    job = context.job
    context.bot.send_message(
        job.context["chat_id"],
        f"⏰ NHẮC VIỆC:\n{job.context['text']}"
    )

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
            f"✅ Đã đặt lịch {time_str} {date_str}"
        )

    except:
        update.message.reply_text("❌ Sai định dạng.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("remindat", remind_at))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
