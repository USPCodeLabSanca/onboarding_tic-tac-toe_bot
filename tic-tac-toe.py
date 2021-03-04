class TicTacToe:
    def __init__(self):
        self.board = [[' ' for i in range (3)] for j in range(3)]
        self.symbols = {
            'x' : 'x',
            'o' : 'o'
        }
        self.count_moves = 0
    
    def __position_is_valid(self, x, y):
        return x >= 0 and x < 3 and y >= 0 and y < 3 and self.board[x][y] == ' '

    def update_game(self, x, y, mark):
        if (mark == 'x' or mark == 'o'):
            if (self.__position_is_valid(x, y)):
                self.board[x][y] = self.symbols[mark]
                self.count_moves+=1
            else:
                raise Exception('Posição Inválida ou Já Preenchida')
        else:
            raise Exception('Símbolo Inválido. Digite \'x\' ou \'o\'')

        self.show_board()

        if (self.__check_game(x, y, mark)):
            print("O jogador com {value} ganhou!!".format(value = self.symbols[mark]))
        elif (self.count_moves == 9):
            print ("Os jogadores empataram!!")
    
    def __check_game(self, x, y, mark):
        i = j = 0
       
        #verifying the vertical orientation
        while (i < 3):
            if (self.board[i][y] != self.symbols[mark]):
                break
            i+=1
        else:
            return True

        #verifying the horizontal orientation
        while (j < 3):
            if (self.board[x][j] != self.symbols[mark]):
                break
            j+=1
        else:
            return True
        
        i = j = 0
        #verifying the right diagonal
        while (i < 3):
            if (self.board[i][j] != self.symbols[mark]):
                break
            i+=1
            j+=1
        else:
            return True
        
        i = 0
        j = 2
        #verifying the left diagonal
        while (i < 3):
            if (self.board[i][j] != self.symbols[mark]):
                break
            i+=1
            j-=1
        else:
            return True
        
        return False
    
    def show_board(self):
        for i in range (3):
            print("|", end = '')
            for j in range (3):
                print ("{value}".format(value = self.board[i][j]), end='|')
            print()
        print()
    
def main():
    game = TicTacToe()
    
    game.update_game(1, 1, 'x')
    game.update_game(1, 2, 'o')
    game.update_game(0, 1, 'x')
    game.update_game(2, 1, 'o')
    game.update_game(0,0, 'o')
    game.update_game(0,2,'o')
    game.update_game(1,0,'x')
    game.update_game(2,0,'o')
    game.update_game(2,2,'x')
    
if __name__ == "__main__":
    main()

