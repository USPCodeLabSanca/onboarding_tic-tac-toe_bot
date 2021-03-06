import telegram as t
import telegram.ext as tex
import logging
from tictactoe import TicTacToe

IKB = t.InlineKeyboardButton
IKM = t.InlineKeyboardMarkup

# Função inicial do jogo
def start(update: t.Update, context: tex.CallbackContext):
    context.user_data['tictactoe'] = TicTacToe()
    # Zera o número de rounds jogados
    context.user_data['rounds'] = 0

    # Cria o teclado
    context.user_data['keyboard'] = [
        [IKB(' ', callback_data='0,0'), IKB(' ', callback_data='0,1'), IKB(' ', callback_data='0,2')],
        [IKB(' ', callback_data='1,0'), IKB(' ', callback_data='1,1'), IKB(' ', callback_data='1,2')],
        [IKB(' ', callback_data='2,0'), IKB(' ', callback_data='2,1'), IKB(' ', callback_data='2,2')]
    ]

    keyboard = context.user_data['keyboard']
    rounds = context.user_data['rounds']
    tictactoe = context.user_data['tictactoe']
    
    # Define a vez de quem vai jogar
    if rounds % 2 == 0:
        simbolo = '❌'
        simbolo_ascii = 'x'
    else:
        simbolo = '⭕️'
        simbolo_ascii = 'o'

    tictactoe.set_symbol(simbolo_ascii, simbolo)
    # Atualiza o context contendo o símbolo do round atual
    context.user_data['simbolo'] = simbolo
    context.user_data['simbolo_ascii'] = simbolo_ascii

    # Mostra a mensagem inicial
    update.message.reply_text("O jogo vai começar!")
    # Mostra o teclado do jogo com o símbolo de quem começará a jogar
    update.message.reply_text(f"Selecione uma posição (seu símbolo é {simbolo})", reply_markup=IKM(keyboard))

    return 'ROUND'

# Loop do jogo
def round(update: t.Update, context: tex.CallbackContext):
    #Aumenta o contador de rounds
    context.user_data['rounds'] = context.user_data['rounds'] + 1

    rounds = context.user_data['rounds']
    keyboard = context.user_data['keyboard']
    simbolo = context.user_data['simbolo']
    simbolo_ascii = context.user_data['simbolo_ascii']
    tictactoe = context.user_data['tictactoe']

    # Aguarda a resposta
    update.callback_query.answer()
    
    # Recebe as coordenadas do botão pressionado
    data = update.callback_query.data
    x, y = [ int(s) for s in data.split(',') ]

    # Caso o botão já tenha sido selecionado, mostrar mensagem de erro
    try:
        result = tictactoe.update_game(x, y, simbolo_ascii)
        keyboard[x][y] = IKB(simbolo, callback_data=data) #(x,y)
    except Exception as e:
        update.callback_query.message.edit_text(str(e) + f"\nSelecione uma posição (seu símbolo é {simbolo})")
        update.callback_query.message.edit_reply_markup(IKM(keyboard))
        context.user_data['rounds'] = context.user_data['rounds'] - 1
        return 'ROUND'

    # Define a "vez" de quem vai jogar
    if rounds % 2 == 0:
        simbolo = '❌'
        simbolo_ascii = 'x'
    else:
        simbolo = '⭕️'
        simbolo_ascii = 'o'
    # Atualiza o context contendo o símbolo do round atual
    context.user_data['simbolo'] = simbolo
    context.user_data['simbolo_ascii'] = simbolo_ascii

    # Atualiza a mensagem contendo o símbolo (de quem é a vez)
    update.callback_query.message.edit_text(f"Selecione uma posição (seu símbolo é {simbolo})")
    # Mostra o teclado do jogo
    update.callback_query.message.edit_reply_markup(IKM(keyboard))

    if result != None:
        update.callback_query.message.reply_text(result)
        return tex.ConversationHandler.END

    return 'ROUND'

def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    updater = tex.Updater(token='1611542237:AAGPMlkeNxp3geL0urxsSsBncnOBROjctsg')
    dp = updater.dispatcher
    
    # Handler do jogo
    game_handler = tex.ConversationHandler(
        entry_points=[tex.CommandHandler('start', start)],
        states={
            'ROUND': [tex.CallbackQueryHandler(round)]
        },
        fallbacks=[tex.CommandHandler('start', start)]
    )
    dp.add_handler(game_handler)
    
    updater.start_polling()
    logging.info("=== Bot running! ===")
    updater.idle()
    logging.info("=== Bot shutting down! ===")

if __name__ == "__main__":
    main()