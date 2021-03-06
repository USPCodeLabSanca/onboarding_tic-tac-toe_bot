import telegram as t
import telegram.ext as tex
import json
import random
from tictactoe import TicTacToe


IKB = t.InlineKeyboardButton
IKM = t.InlineKeyboardMarkup


TOKEN = '1611542237:AAGPMlkeNxp3geL0urxsSsBncnOBROjctsg' # só pra testar


users_file = open('users.json')
game_users = json.load(users_file)
users_file.close()


def random_start(a, b):
    if(random.randint(0,1) == 0):
        return a, b 
    return b, a
  

def nick_exists(nickname):
    for user in game_users:
        if(nickname == user["nickname"]):
            return True
    return False


def invalid_nick(update, context):
    update.message.reply_text(
        "Nickname inválido! Ele NÃO pode começar com '/'. Digite outro:")
    return "SET_NICK"


def search_user_in_list_by_name(username):
    for user in game_users:
        if(username == user["username"]):
            return user
    return None


def search_user_in_list_by_nick(nickname):
    for user in game_users:
        if(nickname == user["nickname"]):
            return user
    return None


def search_user_by_id(users, user_id):
    for user in users:
        if(user_id == user["user_id"]):
            return user
    return None


def remove_user_from_queue(user_id):
    for user in game_users:
        if(user_id == user["user_id"]):
            game_users.remove(user)


def get_user_from_list_start(skip_user_id):
    for user in game_users:
        if user["user_id"] != skip_user_id and user["active"] == True and user["adversary"] == None:
            game_users.remove(user)
            game_users.append(user)
            user["active"] = False
            return user    
    return None


def start(update, context):
    if search_user_by_id(game_users, update.effective_user.id) != None:
        update.message.reply_text(
            "Você já está presente no jogo! Digite /play para ir para o menu!")
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

    for user in game_users:
        if my_user_id == user["user_id"]:
            user["nickname"] = my_nick
            update.message.reply_text('Nickname modificado com sucesso!')
            return tex.ConversationHandler.END

    user_object = {
        "user_id": my_user_id,
        "username": my_username,
        "nickname": my_nick,
        "active": False,
        "adversary": None,
        "listening": False
    }

    game_users.append(user_object)

    text = f'Muito bem, {my_nick}. '
    text += 'Digite /play para ir para o menu do jogo ou aguarde ser chamado para uma partida'
    update.message.reply_text(text)
    return tex.ConversationHandler.END


def change_nick(update, context):
    if search_user_by_id(game_users, update.effective_user.id) == None:
        update.message.reply_text("Impossível mudar seu apelido! Dê o comando /start para iniciar.")
        return tex.ConversationHandler.END
    update.message.reply_text("Digite o novo nickname.")
    return "SET_NICK"


def users(update, context):
    users = []

    for user in game_users:
        if(user["active"] == True and user["adversary"] == None and update.effective_user.id != user["user_id"]): 
            users.append(user['nickname'])

    if len(users) > 0:
        update.message.reply_text('Atualmente, esses são os outros usuários presentes na fila:')
        text = "\n".join(users)
    else:
        text = 'Parece que não há ninguém por aqui'

    context.bot.sendMessage(chat_id=update.effective_chat.id, text=text)


def play_command(update, context):
    options = []
    user = search_user_by_id(game_users, update.effective_user.id)

    if user == None:
        update.message.reply_text('Você não está cadastrado! Digite /start para continuar')
        return tex.ConversationHandler.END

    if user["active"] == False:
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

    existing_user = search_user_by_id(game_users, user_id)

    if existing_user == None:
        text = 'Você ainda não está cadastrado! Dê /start para começar'
        return tex.ConversationHandler.END

    if existing_user["active"] == False and user_input == 'Entrar na fila':
        existing_user["active"] = True
        existing_user["listening"] = True
        text = 'Você entrou na fila de espera do jogo! Aguarde ser chamado para uma partida. '
        context.bot.sendMessage(chat_id=user_id, text=text)
        text = 'Se quiser sair da fila, vá para o menu do jogo com /play e selecione \'Sair da fila\'.'
        context.bot.sendMessage(chat_id=user_id, text=text)
        return "ROUND"
    
    if user_input == 'Sair da fila':
        return remove_user(update, context)

    if user_input == 'Jogar (usuário aleatório)':
        user = search_user_by_id(game_users, user_id)
        if user["adversary"] != None:
            text = f'Você já está presente em uma partida! Finalize-a antes de começar uma nova!'
            context.bot.sendMessage(chat_id=user_id, text=text)
            return 'ROUND'
        return random_user(update, context)

    if user_input == 'Jogar (usuário específico)':
        user = search_user_by_id(game_users, user_id)
        if user["adversary"] != None:
            text = f'Você já está presente em uma partida! Finalize-a antes de começar uma nova!'
            context.bot.sendMessage(chat_id=user_id, text=text)
            return 'ROUND'
        text = 'Digite o nickname de seu adversário'
        context.bot.sendMessage(chat_id=user_id, text=text)
        return 'SPECIFIC_USER'

    text = 'Opção inválida!'
    context.bot.sendMessage(chat_id=user_id, text=text)
    return 'CHECK_OPTION'
    

def init_game(update, context, player2):

    player1_id = update.effective_user.id

    player1 = search_user_by_id(game_users, player1_id)

    player1, player2 = random_start(player1, player2)

    text1 = f'{player1["username"]}, você vai jogar com {player2["username"]}, você começa jogando.'
    text2 = f'{player2["username"]}, você vai jogar com {player1["username"]}, você começa esperando.'
    context.bot.sendMessage(chat_id=player1["user_id"], text=text1)
    context.bot.sendMessage(chat_id=player2["user_id"], text=text2)
    
    player1["active"] = True
    player1["listening"] = False
    player1["adversary"] = player2["user_id"]
    player1["symbol_ascii"] = "x"
    player1["symbol"] = "❌"
    player1["key"] = str(player1["user_id"]) + str(player2["user_id"])

    player2["active"] = True
    player2["listening"] = True
    player2["adversary"] = player1["user_id"]
    player2["symbol_ascii"] = "o"
    player2["symbol"] = "⭕️"
    player2["key"] = str(player1["user_id"]) + str(player2["user_id"])

    game = TicTacToe()
    kbd = [
            [IKB(' ', callback_data='0,0'), IKB(' ', callback_data='0,1'), IKB(' ', callback_data='0,2')],
            [IKB(' ', callback_data='1,0'), IKB(' ', callback_data='1,1'), IKB(' ', callback_data='1,2')],
            [IKB(' ', callback_data='2,0'), IKB(' ', callback_data='2,1'), IKB(' ', callback_data='2,2')]
        ]
    
    context.bot_data[str(player1["user_id"]) + str(player2["user_id"])] = {
        "tictactoe": game,
        "keyboard": kbd
    }
    
    game.set_symbol(player1["symbol_ascii"], player1["symbol"])
    game.set_symbol(player2["symbol_ascii"], player2["symbol"])
    
    # Mostra o teclado do jogo com o símbolo de quem começará a jogar
    textp1 = f"Selecione uma posição (seu símbolo é {player1['symbol']})"
    player1["last_message"] = context.bot.sendMessage(chat_id=player1["user_id"], text=textp1, reply_markup=IKM(kbd))
    return "ROUND"


def random_user(update, context):

    player1_id = update.effective_user.id

    player2 = get_user_from_list_start(player1_id)

    if player2 == None:
        text = 'Parece que você está sozinho por aqui. Não há usuários disponíveis. '
        text += 'Compartilhe o bot com os amigos para poder jogar.'
        update.message.reply_text(text)
        return tex.ConversationHandler.END

    return init_game(update,context, player2)


def specific_user(update, context):
    player1_id = update.effective_user.id
    
    player2 = search_user_in_list_by_nick(update.message.text)
    
    if player2 == None:
        text = 'Não foi encontrado nenhum usuário com esse apelido!'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END

    if player2["user_id"] == player1_id:
        text = 'Você não pode jogar consigo mesmo!'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END

    if player2["active"] == False:
        text = f'{player2["nickname"]} não quer jogar agora!'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END

    if player2["adversary"] != None:
        text = f'{player2["nickname"]} está no meio de uma partida.'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END
        
    return init_game(update, context, player2)
    

def gameRound(update, context):
    update.callback_query.answer()

    user_id = update.effective_user.id

    user = search_user_by_id(game_users, user_id)
    adversary = search_user_by_id(game_users, user["adversary"])

    game = context.bot_data[user["key"]]
    
    # Recebe as coordenadas do botão pressionado
    data = update.callback_query.data
    x, y = [ int(s) for s in data.split(',') ]

    # Caso o botão já tenha sido selecionado, mostrar mensagem de erro
    try:
        result = game["tictactoe"].update_game(x, y, user["symbol_ascii"])
        game["keyboard"][x][y] = IKB(user["symbol"], callback_data=data) #(x,y)
    except Exception as e:
        update.callback_query.message.edit_text(str(e) + f"\nSelecione uma posição (seu símbolo é {user['symbol']})")
        update.callback_query.message.edit_reply_markup(IKM(game["keyboard"]))
        return 'ROUND'

    context.bot.deleteMessage(chat_id=user["user_id"], message_id=user["last_message"].message_id)
    text_adversary = f"Selecione uma posição (seu símbolo é {adversary['symbol']})"
    adversary["last_message"] = context.bot.sendMessage(chat_id=adversary["user_id"], text=text_adversary, reply_markup=IKM(game["keyboard"]))

    if result != None:
        user_text = ''
        adversary_text = ''

        if result == user["symbol"]:
            user_text = 'Você venceu!'
            adversary_text = f'{user["nickname"]} venceu!'
        elif result == adversary["symbol"]:
            user_text = f'{adversary["nickname"]} venceu!'
            adversary_text = 'Você venceu!'
        else:
            user_text = adversary_text = 'Deu velha!'

        context.bot.sendMessage(chat_id=user["user_id"], text=user_text)
        context.bot.sendMessage(chat_id=adversary["user_id"], text=adversary_text)

        user["active"] = False
        adversary["active"] = False
        user["listening"] = False
        adversary["listening"] = False
        user["adversary"] = None
        adversary["adversary"] = None
        user["key"] = None
        adversary["key"] = None
        return tex.ConversationHandler.END

    if user["active"] == False:
        return remove_user(update, context)

    if user["listening"] == True:
        update.callback_query.message.reply_text("Você deve esperar pelo adversário")
        return "ROUND"

    adversary["listening"] = False
    user["listening"] = True

    return "ROUND"
    

def remove_user(update, context):
    existingPlayer = search_user_by_id(game_users, update.effective_user.id)

    if existingPlayer == None:
        text = 'Você não estava cadastrado. Digite /start para continuar'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END

    if existingPlayer["adversary"] != None:
        text = 'Você não pode sair no meio de uma partida!'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return 'ROUND'

    else:
        existingPlayer["active"] = False
        text = 'Para retornar ao menu do jogo, digite /play'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)

    return tex.ConversationHandler.END


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
        'CHECK_OPTION': [tex.MessageHandler(tex.Filters.text & ~tex.Filters.command, check_option)],
        'SPECIFIC_USER': [tex.MessageHandler(tex.Filters.text & ~tex.Filters.command, specific_user)],
        'ROUND': [tex.CallbackQueryHandler(gameRound)]
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

dispatcher.add_handler(change_nick_handler)
dispatcher.add_handler(play_handler)
dispatcher.add_handler(users_handler)
dispatcher.add_handler(start_handler)

updater.start_polling()

print("The bot is now running!")
updater.idle()
print("The bot is now shutting down...")