import telegram
import telegram.ext as tex
import json

users_file = open('users.json')
users_queue = json.load(users_file)


def start(update, context):
    update.message.reply_text("Bem-vindo(a/e)! Escolha um nickname:")
    return "SET_NICK"


def set_nick(update, context):
    my_nick = update.message.text
    my_username = update.effective_user.name
    my_user_id = update.effective_user.id

    user_object = {
        "user_id": my_user_id,
        "username": my_username,
        "nickname": my_nick
    }

    users_queue.append(user_object)
    return tex.ConversationHandler.END


def invalid_nick(update, context):
    update.message.reply_text(
        "Nickname inválido! Ele NÃO pode começar com '/'. Digite outro:")
    return "SET_NICK"


def users(update, context):
    users = []

    for user in users_queue:
        users.append(user['nickname'])

    text_user_list = "\n".join(users)

    context.bot.sendMessage(
        chat_id=update.effective_chat.id, text=text_user_list)


updater = tex.Updater('1297400305:AAGjXuYCv00jzjaiCpDQSsl8G6TDLXkx_Cs')
dispatcher = updater.dispatcher

start_handler = tex.ConversationHandler(
    entry_points=[tex.CommandHandler('start', start)],
    states={
        "SET_NICK": [tex.MessageHandler(tex.Filters.text & ~tex.Filters.command, set_nick)]
    },
    fallbacks=[tex.MessageHandler(tex.Filters.all, invalid_nick)]
)

users_handler = tex.CommandHandler('users', users)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(users_handler)

updater.start_polling()

print("The bot is now running!")
updater.idle()
print("The bot is now shutting down...")
