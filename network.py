import telegram as t
import telegram.ext as tex
import json

TOKEN = '1611542237:AAGPMlkeNxp3geL0urxsSsBncnOBROjctsg' # só pra testar

users_file = open('users.json')
users_queue = json.load(users_file)
users_file.close()


def start(update, context):
    if search_user_in_queue_by_id(update.effective_user.id) != None:
        update.message.reply_text("Você já está presente na fila")
        return tex.ConversationHandler.END
    update.message.reply_text("Bem-vindo(a/e)! Escolha um nickname:")
    return "SET_NICK"


def set_nick(update, context):
    my_nick = update.message.text
    my_username = update.effective_user.name
    my_user_id = update.effective_user.id

    if nick_exists(my_nick):
        update.message.reply_text("Esse nick já existe, por favor digite outro")
        return "SET_NICK"

    user_object = {
        "user_id": my_user_id,
        "username": my_username,
        "nickname": my_nick
    }

    for user in users_queue:
        if my_user_id == user["user_id"]:
            user["nickname"] = my_nick
            update_queue_json_file()
            update.message.reply_text('Nickname modificado com sucesso!')
            return tex.ConversationHandler.END

    #users_queue.append(user_object)
    #update_queue_json_file()

    text = f'Muito bem, {my_nick}. Digite /play para ir para o menu do jogo ou aguarde ser chamado para uma partida'
    update.message.reply_text(text)
    return tex.ConversationHandler.END


def change_nick(update, context):
    if search_user_in_queue(update.effective_user.name) == None:
        update.message.reply_text("Impossível mudar seu apelido! Você não está cadastrado na fila de espera.")
        return tex.ConversationHandler.END
    update.message.reply_text("Digite o novo nickname.")
    return "SET_NICK"


def nick_exists(nickname):
    for user in users_queue:
        if(nickname == user["nickname"]):
            return True
    return False


def invalid_nick(update, context):
    update.message.reply_text(
        "Nickname inválido! Ele NÃO pode começar com '/'. Digite outro:")
    return "SET_NICK"


def users(update, context):
    users = []

    update.message.reply_text('Atualmente, esses são os usuários presentes na fila:')


    for user in users_queue:
        if(update.effective_user.id != user["user_id"]): 
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


def search_user_in_queue_by_nick(nickname):
    for user in users_queue:
        if(nickname == user["nickname"]):
            return user
    return None


def search_user_in_queue_by_id(user_id):
    for user in users_queue:
        if(user_id == user["user_id"]):
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
        text = 'Digite o nickname de seu adversário'
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
    player1_id = update.effective_user.id
    player1_name = update.effective_user.name
    player2 = get_user_from_queue_start(update.effective_user.id)
    text = ''
    if player2 == None:
        text = 'Parece que você está sozinho por aqui. Não há usuários disponíveis. '
        text += 'Compartilhe o bot com os amigos para poder jogar.'
    else:
        text1 = f'{player1_name}, você vai jogar com {player2["username"]}'
        text2 = f'{player2["username"]}, você vai jogar com {player1_name}'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text1)
        context.bot.sendMessage(chat_id=player2["user_id"], text=text2)
        # função do jogo
        text = 'Você jogou com um usuário aleatório. Retorno com sucesso'
        context.bot.sendMessage(chat_id=player2["user_id"], text=text)
    context.bot.sendMessage(chat_id=player1_id, text=text)
    return tex.ConversationHandler.END


def specific_user(update, context):
    player1_id = update.effective_user.id
    player1_username = update.effective_user.name
    player2 = search_user_in_queue_by_nick(update.message.text)
    if player2 == None:
        text = 'Não foi encontrado nenhum usuário com esse nome na fila'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END
    elif player2["user_id"] == player1_id:
        text = 'Você não pode jogar consigo mesmo!'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END
    text1 = f'{player1_username}, você vai jogar com {player2["username"]}'
    text2 = f'{player2["username"]}, você vai jogar com {player1_username}'
    context.bot.sendMessage(chat_id=player1_id, text=text1)
    context.bot.sendMessage(chat_id=player2["user_id"], text=text2)
    # função do jogo
    text = 'Você jogou com um usuário específico. Retorno com sucesso'
    context.bot.sendMessage(chat_id=player1_id, text=text)
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

change_nick_handler = tex.ConversationHandler(
    entry_points = [tex.CommandHandler("change", change_nick)],
    states={
        "SET_NICK": [tex.MessageHandler(tex.Filters.text & ~tex.Filters.command, set_nick)]
    },
    fallbacks=[tex.MessageHandler(tex.Filters.all, invalid_nick)]
)

users_handler = tex.CommandHandler('users', users)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(play_handler)
dispatcher.add_handler(users_handler)
dispatcher.add_handler(change_nick_handler)

updater.start_polling()

print("The bot is now running!")
updater.idle()
print("The bot is now shutting down...")
