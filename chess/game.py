from sys import platform
if platform == "darwin":
    from tkmacosx import Button
    from tkinter import Tk, Toplevel, Label, StringVar
    square_width = square_height = 50
    board_dimension = "400x400"
else:
    from tkinter import *
    square_width = 3
    square_height = 0
    board_dimension = "700x700"
from .pieces import *
from .constants import *
from .board import *


class PromotionPopup(Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Promotion")
        self.geometry("200x250")
        self.result = None

        self.promotion_label = Label(self, text="Choose promotion:")
        self.promotion_label.pack(pady=10)

        self.promotion_choice = PieceType.QUEEN

        promotion_buttons = [
            ("Queen", PieceType.QUEEN),
            ("Rook", PieceType.ROOK),
            ("Bishop", PieceType.BISHOP),
            ("Knight", PieceType.KNIGHT)
        ]

        for text, piece_type in promotion_buttons:
            button = Button(self, text=text, command=lambda p=piece_type: self.set_promotion_choice(p))
            button.pack(pady=5)

    def set_promotion_choice(self, piece_type):
        self.result = piece_type
        self.destroy()


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
        self.geometry(board_dimension)
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

    def redraw_board(self):
        for rank in range(8):
            for file in range(8):
                piece = self.chessboard[get_square(rank, file)]
                color = "gray" if (rank + file) % 2 == 1 else "black"
                if self.selected_square != None and self.selected_square == get_square(rank, file):
                    color = "lightyellow"
                self.board[rank][file].configure(bg=color, text=piece_unicode(piece.piece_type), fg="white" if piece.color == Color.WHITE else "blue",font=(None, "35"))
        pass
    def square_click(self, rank, file):
        piece = self.chessboard[get_square(rank, file)]
        past_selected_square = self.selected_square
        move_made = False
        if self.selected_square:
            selected_piece = self.chessboard[self.selected_square]
            # print(self.chessboard.legal_moves)
            if selected_piece.symbol() != "_" and selected_piece.color == self.chessboard.turn:
                # A current piece is selected
                try:
                    move = Move(self.selected_square, get_square(rank, file))
                    if self.chessboard[self.selected_square].piece_type == PieceType.PAWN and \
                            (rank == 0 or rank == 7):
                        move.promotion = PieceType.QUEEN # If promoted, king is not in check and move is legal
                    if self.chessboard.is_legal(move):
                        if self.chessboard[self.selected_square].piece_type == PieceType.PAWN and \
                                (rank == 0 or rank == 7):
                            move.promotion = self.show_promotion_popup()
                        self.chessboard.push(move)
                        self.selected_square = None
                        move_made = True
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
        if move_made or past_selected_square != self.selected_square:
            self.redraw_board()

    def show_promotion_popup(self):
        promotion_popup = PromotionPopup(self)
        self.freeze_board()
        self.wait_window(promotion_popup)
        self.unfreeze_board()
        return promotion_popup.result

    def freeze_board(self):
        for row in range(8):
            for col in range(8):
                self.board[row][col].configure(state="disabled")

    def unfreeze_board(self):
        for row in range(8):
            for col in range(8):
                self.board[row][col].configure(state="normal")

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