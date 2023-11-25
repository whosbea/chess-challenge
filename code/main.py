import chess
import chess.pgn
import chess.svg
import chess.engine
from IPython.display import display, SVG


valores_pecas = {'p': 1, "P": 1, 'n': 3, "N": 3,
                 'b': 3, "B": 3, 'k': 5, "K": 5, 'q': 9, "Q": 9}

board = chess.Board()

#printa o tabuleiro
def print_chess_board(board, size=400):
    svg_data = chess.svg.board(board=board, size=size)
    display(SVG(svg_data))


#codigo base para jogar
def realizar_jogada(tabuleiro, movimento):
    if movimento in tabuleiro.legal_moves:
        tabuleiro.push(movimento)
        print(f"\nMovimento: {movimento.uci()}")
        print_chess_board(tabuleiro)
        return True
    else:
        print(f"\nMovimento inválido: {movimento.uci()}")
        return False


def ler_movimentos_do_dataset(file_path):
    movimentos = []

    with open(file_path, 'r') as dataset_file_path:
        # loop infinito ate ler totalmente o arquivo
        while True:
            # Lê um jogo no arquivo
            jogo = chess.pgn.read_game(dataset_file_path)
            if jogo is None:
                break

            for movimento in jogo.mainline_moves():
                # add cada movimento na lista
                movimentos.append(movimento)

    return movimentos

#função que usa o stockfish para fazer a jogada
def stockfish(tabuleiro, engine):
    with chess.engine.SimpleEngine.popen_uci("C:\\Users\\xbea3\\Desktop\\chess challenge\\stockfish-windows-x86-64-avx2\\stockfish\\stockfish-windows-x86-64-avx2.exe") as engine:
        # clone do tabuleiro
        tabuleiro_clone = tabuleiro.copy()
        # avalia melhor jogada
        resultado = engine.play(tabuleiro_clone, chess.engine.Limit(time=2.0))
        movimento_escolhido = resultado.move

        print(f"Stockfish escolheu o movimento: {movimento_escolhido.uci()}")

        if resultado.move in tabuleiro_clone.legal_moves:
            # faz a jogada no tabuleiro original
            tabuleiro.push(movimento_escolhido)
        print_chess_board(tabuleiro)


def jogar():
    tabuleiro = chess.Board()
    print("Tabuleiro inicial:")
    print_chess_board(tabuleiro)

    engine = chess.engine.SimpleEngine.popen_uci("C:\\Users\\xbea3\\Desktop\\chess challenge\\stockfish-windows-x86-64-avx2\\stockfish\\stockfish-windows-x86-64-avx2.exe")

    caminho_dataset = r'C:\\Users\\xbea3\\Desktop\\chess challenge\\code\\dt\\ficsgamesdb_202301_chess_nomovetimes_311246.pgn'

    # ler_movimentos_do_dataset(caminho_dataset)

    while not tabuleiro.is_game_over():
        if tabuleiro.turn == chess.WHITE:
            # Vez das brancas
            user_input = input(
                "Jogada (em formato UCI, ex: 'e2e4'): ")
            user_move = chess.Move.from_uci(user_input)

            if realizar_jogada(tabuleiro, user_move):
                print("A jogada das brancas foi: " + user_input)
            else:
                print("Movimento inválido. Tente novamente.")
        else:
            # Vez das pretas: escolher um movimento inteligente
            stockfish(tabuleiro, engine)

    print("O jogo acabou.")
    if tabuleiro.is_checkmate():
        print("Xeque-mate!")
    elif tabuleiro.is_stalemate():
        print("Empate por afogamento.")
    elif tabuleiro.is_insufficient_material():
        print("Empate por material insuficiente.")
    elif tabuleiro.is_seventyfive_moves():
        print("Empate por regra dos 75 movimentos.")
    elif tabuleiro.is_fivefold_repetition():
        print("Empate por repetição de posição.")

    engine.quit()


jogar()
