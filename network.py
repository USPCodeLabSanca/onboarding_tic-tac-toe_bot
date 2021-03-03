import telegram as t
import telegram.ext as tex
import json

TOKEN = '1611542237:AAGPMlkeNxp3geL0urxsSsBncnOBROjctsg' # só pra testar

users_file = open('users.json')
users_queue = json.load(users_file)
users_file.close()


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

    existingUser = search_user_in_queue(my_username)

    if(existingUser != None):
        update.message.reply_text('Seu nickname foi atualizado!')
        remove_user_from_queue(my_user_id)

    users_queue.append(user_object)
    update_queue_json_file()

    text = f'Muito bem, {my_nick}. Digite /play para iniciar uma partida ou aguarde ser chamado por um outro jogador'
    update.message.reply_text(text)
    return tex.ConversationHandler.END


def invalid_nick(update, context):
    update.message.reply_text(
        "Nickname inválido! Ele NÃO pode começar com '/'. Digite outro:")
    return "SET_NICK"


def users(update, context):
    users = []

    update.message.reply_text('Atualmente, esses são os usuários presentes na fila:')

    for user in users_queue:
        users.append(user['nickname'])

    text_user_list = "\n".join(users)

    context.bot.sendMessage(
        chat_id=update.effective_chat.id, text=text_user_list)


def update_queue_json_file():
    users_file = open('users.json', "w")
    json.dump(users_queue, users_file, indent=2)
    users_file.close()


def search_user_in_queue(username):
    for user in users_queue:
        if(username == user["username"]):
            return user
    return None


def remove_user_from_queue(user_id):
    for user in users_queue:
        if(user_id == user["user_id"]):
            users_queue.remove(user)
            update_queue_json_file()


def get_user_from_queue_start(skip_user_id):
    len_queue = len(users_queue)

    if len_queue == 0:
        return None
    
    if users_queue[0]["user_id"] == skip_user_id:
        if len_queue >= 2:
            copy = users_queue[1]
            users_queue.remove(users_queue[1])
            users_queue.append(copy)
            update_queue_json_file()
            return copy
        return None

    copy = users_queue[0] 
    users_queue.remove(users_queue[0])
    users_queue.append(copy)
    update_queue_json_file()
    return copy 


def play_command(update, context):
    options = []
    if search_user_in_queue(update.effective_user.name) == None:
        options.append(['Entrar na fila'])
    else:
        options.append(['Sair da fila'])
    options.append(['Jogar (usuário aleatório)'])
    options.append(['Jogar (usuário específico)'])
    keyboard = t.ReplyKeyboardMarkup(options, one_time_keyboard=True)
    text = 'Selecione uma opção:'
    user_id = update.effective_user.id
    update.message.reply_text(text, reply_markup=keyboard)
    return 'CHECK_OPTION' 


def check_option(update, context):
    user_input = update.message.text 
    user_id = update.effective_user.id
    if search_user_in_queue(update.effective_user.name) == None:
        if user_input == 'Entrar na fila':
            text = 'Entrando na fila...'
            context.bot.sendMessage(chat_id=user_id, text=text)
            return start(update, context)
    if user_input == 'Sair da fila':
        text = 'Saindo da fila...'
        context.bot.sendMessage(chat_id=user_id, text=text)
        return remove_user(update, context)
    elif user_input == 'Jogar (usuário aleatório)':
        text = 'Você vai jogar com um usuário aleatório'
        context.bot.sendMessage(chat_id=user_id, text=text)
        return random_user(update, context)
    elif user_input == 'Jogar (usuário específico)':
        text = 'Você vai jogar com um usuário específico'
        context.bot.sendMessage(chat_id=user_id, text=text)
        text = 'Digite o @ de seu adversário'
        context.bot.sendMessage(chat_id=user_id, text=text)
        return 'SPECIFIC_USER'
    else:
        text = 'Opção inválida!'
        context.bot.sendMessage(chat_id=user_id, text=text)
        return 'CHECK_OPTION'
    return tex.ConversationHandler.END


def remove_user(update, context):
    existingPlayer = search_user_in_queue(update.effective_user.name)
    if existingPlayer == None:
        text = 'Você não estava incluído na fila. Digite /start para continuar'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END
    else:
        remove_user_from_queue(existingPlayer["user_id"])
        text = 'Seu nome foi excluído da fila do jogo!'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
    return tex.ConversationHandler.END


def random_user(update, context):
    player1 = search_user_in_queue(update.effective_user.name)
    player2 = get_user_from_queue_start(update.effective_user.id)
    text = ''
    if(player2 == None):
        text = 'Parece que você está sozinho por aqui. Não há usuários disponíveis. '
        text += 'Compartilhe o bot com os amigos para poder jogar.'
    else:
        text1 = f'{player1["username"]}, você vai jogar com {player2["username"]}'
        text2 = f'{player2["username"]}, você vai jogar com {player1["username"]}'
        context.bot.sendMessage(chat_id=player1["user_id"], text=text1)
        context.bot.sendMessage(chat_id=player2["user_id"], text=text2)
        # função do jogo
        text = 'Você jogou com um usuário aleatório. Retorno com sucesso'
        context.bot.sendMessage(chat_id=player2["user_id"], text=text)
    context.bot.sendMessage(chat_id=player1["user_id"], text=text)
    return tex.ConversationHandler.END


def specific_user(update, context):
    player1 = search_user_in_queue(update.effective_user.name)
    player2 = search_user_in_queue(update.message.text)
    if(player2 == None):
        text = 'Não foi encontrado nenhum usuário com esse nome na fila'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END
    elif player2["user_id"] == player1["user_id"]:
        text = 'Você não pode jogar consigo mesmo!'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END
    # função do jogo
    text1 = f'{player1["username"]}, você vai jogar com {player2["username"]}'
    text2 = f'{player2["username"]}, você vai jogar com {player1["username"]}'
    context.bot.sendMessage(chat_id=player1["user_id"], text=text1)
    context.bot.sendMessage(chat_id=player2["user_id"], text=text2)
    text = 'Você jogou com um usuário específico. Retorno com sucesso'
    context.bot.sendMessage(chat_id=player1["user_id"], text=text)
    context.bot.sendMessage(chat_id=player2["user_id"], text=text)
    return tex.ConversationHandler.END


#updater = tex.Updater('1297400305:AAGjXuYCv00jzjaiCpDQSsl8G6TDLXkx_Cs')
updater = tex.Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher

start_handler = tex.ConversationHandler(
    entry_points=[tex.CommandHandler('start', start)],
    states={
        "SET_NICK": [tex.MessageHandler(tex.Filters.text & ~tex.Filters.command, set_nick)]
    },
    fallbacks=[tex.MessageHandler(tex.Filters.all, invalid_nick)]
)

play_handler = tex.ConversationHandler(
    entry_points=[tex.CommandHandler("play", play_command)],
    states={
        'CHECK_OPTION': [tex.MessageHandler(tex.Filters.text, check_option)],
        'SET_NICK': [tex.MessageHandler(tex.Filters.text & ~tex.Filters.command, set_nick)],
        'SPECIFIC_USER': [tex.MessageHandler(tex.Filters.text, specific_user)]
    },
    fallbacks=[tex.CommandHandler("play", play_command)]
)

users_handler = tex.CommandHandler('users', users)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(play_handler)
dispatcher.add_handler(users_handler)

updater.start_polling()

print("The bot is now running!")
updater.idle()
print("The bot is now shutting down...")
