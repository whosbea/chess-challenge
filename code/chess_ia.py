import chess
import chess.pgn
import chess.svg
import chess.engine
from IPython.display import display, SVG
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import pickle
import os

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

def tabuleiro_para_matriz(board):
    matriz = np.zeros((8, 8, 6), dtype=np.uint8)
    for r in range(8):
        for c in range(8):
            piece = board.piece_at(chess.square(c, 7 - r))
            if piece is not None:
                matriz[r, c, piece.piece_type - 1] = int(piece.color)
    return matriz

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

def processar_dataset(data):
    X = [] #matriz do estado do tabuleiro de xadrez 
    y = [] # vetor que contém as jogadas correspondentes a cada estado do tabuleiro
    board = chess.Board()

    for move in data:
        #lista de strings com jogadas
        legal_moves = [str(legal_move) for legal_move in board.legal_moves]

        # Verifica se a jogada atual está entre as jogadas legais
        if move.uci() in legal_moves:
            X.append(tabuleiro_para_matriz(board))
            y.append(move.uci())
            board.push(move)

    return np.array(X), np.array(y)

def construir_rede_neural():
    model = models.Sequential()
    model.add(layers.Conv2D(64, (3, 3), activation='relu', input_shape=(8, 8, 6)))
    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def treinar_modelo(X, y):
    model = construir_rede_neural()
    model.fit(X, y, epochs=10, batch_size=64, validation_split=0.2)
    return model

def salvar_dados_treinamento(model, X, y, caminho_salvamento):
    dados_treinamento = {'modelo': model, 'X': X, 'y': y}

    with open(caminho_salvamento, 'wb') as arquivo:
        pickle.dump(dados_treinamento, arquivo)

    print(f"Dados de treinamento salvos em {caminho_salvamento}")

def treinar_ia(caminho_dataset, caminho_salvamento):
    # Verifica se já existem dados de treinamento salvos
    if os.path.exists(caminho_salvamento):
        print("Carregando dados de treinamento existentes...")
        model, X, y = carregar_dados_treinamento(caminho_salvamento)
    else:
        print("Nenhum dado de treinamento encontrado. Treinando a IA...\n")
        print("Lendo movimentos do dataset...\n")
        chess_data = ler_movimentos_do_dataset(caminho_dataset)
        print("Processando dataset...\n")
        X, y = processar_dataset(chess_data)
        print("Treinando modelo...\n")
        model = treinar_modelo(X, y)
        print("Treinamento concluído.")
        # Salva os dados de treinamento
        salvar_dados_treinamento(model, X, y, caminho_salvamento)
    
    return model

def carregar_dados_treinamento(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as arquivo:
        dados_treinamento = pickle.load(arquivo)
    
    return dados_treinamento['modelo'], dados_treinamento['X'], dados_treinamento['y']

if __name__ == "__main__":
    caminho_dataset = r'C:\\Users\\xbea3\\Desktop\\chess challenge\\chess-challenge\\code\\dt\\ficsgamesdb_202301_chess_nomovetimes_311246.pgn'
    caminho_salvamento = r'C:\\Users\\xbea3\\Desktop\\chess challenge\\chess-challenge\\code\\treinamento b-iadados_treinamento.pkl'

    model = treinar_ia(caminho_dataset, caminho_salvamento)

