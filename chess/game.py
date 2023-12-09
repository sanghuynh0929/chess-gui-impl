from sys import platform
if platform == "darwin":
    from tkmacosx import Button
    from tkinter import Tk, Frame, Label, Listbox
    square_width = square_height = 50
else:
    from tkinter import *
    square_width = 1
    square_height = 1
from pieces import *
from constants import *
from board import *


class ChessButton(Button):
    def __init__(self, master=None, piece=None, **kwargs):
        super().__init__(master, **kwargs)
        self.piece = piece
        self.configure(text=piece_unicode(piece.piece_type), fg="white" if piece.color == Color.WHITE else "blue",font=(None, "35"))

class ChessBoard(Tk):
    def __init__(self):
        super().__init__()
        self.selected_square = None
        self.title("Chess Board")
        self.geometry("400x400")
        self.resizable(False, False)
        self.create_board()

    def create_board(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.chessboard = Board()
        self.draw_board()


    def draw_board(self):
        for rank in range(8):
            for file in range(8):
                color = "gray" if (rank + file) % 2 == 1 else "black"
                if self.selected_square != None and self.selected_square == get_square(rank, file):
                    color = "lightyellow"
                piece = self.chessboard[get_square(rank, file)]
                square = ChessButton(self, piece=piece, bg=color, width=square_width, height=square_height, borderwidth=0, highlightthickness=0,
                                     command=lambda r=rank, c=file: self.square_click(r, c))
                square.grid(row=7-rank, column=file)
                self.board[rank][file] = square

    def square_click(self, rank, file):
        piece = self.chessboard[get_square(rank, file)]
        if self.selected_square:
            selected_piece = self.chessboard[self.selected_square]
            # print(self.chessboard.legal_moves)
            if selected_piece.symbol() != "_" and selected_piece.color == self.chessboard.turn:
                # A current piece is selected
                try:
                    move = Move(self.selected_square, get_square(rank, file))
                    if self.chessboard.is_legal(move):
                        self.chessboard.push(move)
                        self.selected_square = None
                    else:
                        raise IllegalMoveError("Illegal move")
                except GameTerminatedError:
                    self.selected_square = None
                except IllegalMoveError:
                    self.selected_square = None
            elif piece.symbol() != "_" and piece.color == self.chessboard.turn:
                self.selected_square = get_square(rank, file)
        else:
            if piece != Piece.from_symbol("_") and piece.color == self.chessboard.turn:
                self.selected_square = get_square(rank, file)
        self.draw_board()
        # print(self.selected_square)
        # print(self.chessboard.legal_moves)
def piece_unicode(piece_type):
    symbols = {
        PieceType.EMPTY: ' ',
        PieceType.PAWN: '♟',
        PieceType.KNIGHT: '♞',
        PieceType.BISHOP: '♝',
        PieceType.ROOK: '♜',
        PieceType.QUEEN: '♛',
        PieceType.KING: '♚',
    }
    return symbols[piece_type]


def start_game():
    chess_board = ChessBoard()
    chess_board.mainloop()