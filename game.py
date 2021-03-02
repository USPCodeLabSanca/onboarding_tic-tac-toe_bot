import telegram
import telegram.ext as tex


def start(update, context):
    update.message.reply_text("Bem-vindo(a/e)!")


updater = tex.Updater('1297400305:AAGjXuYCv00jzjaiCpDQSsl8G6TDLXkx_Cs')
dispatcher = updater.dispatcher

start_handler = tex.CommandHandler('start', start)

dispatcher.add_handler(start_handler)

updater.start_polling()

print("The bot is now running!")
updater.idle()
print("The bot is now shutting down...")
