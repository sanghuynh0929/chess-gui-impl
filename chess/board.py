from typing import Optional, Iterator, List
from copy import deepcopy

from moves import *
from constants import *
from pieces import *

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
STARTING_BOARD_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


class LegalMoveWrapper:
    # Inner class of Board; wraps LegalMove so that for each turn, legal move list is only calculated once
    def __init__(self, board):
        self.board = deepcopy(board)
        self.fullmove_number = board.fullmove_number
        self.turn = board.turn
        self.legal_moves_list = self.board.generate_legal_moves()

    def __len__(self):
        return len(self.legal_moves_list)

    def __iter__(self) -> Iterator[Move]:
        return self.legal_moves_list

    def __contains__(self, move: Move) -> bool:
        # Update this
        return move in self.legal_moves_list

    def __repr__(self):
        return f"<LegalMoveGenerator at {id(self):#x}; list={self.legal_moves_list})>"

class Board:
    def __init__(self):
        self.board: List[List[Piece]] = [[Piece(PieceType('_'), Color(0)) for _ in range(8)] for _ in range(8)]
        self.turn: Color = Color.WHITE
        self.castling_right: dict = {'K' : False, 'k' : False, 'Q' : False, 'q' : False}     # Castling rights for both players
        self.fullmove_number: int = 1    # Increment by one after each black's turn
        self.halfmove_clock: int = 0     # Counter for 50-move draw rule
        self.ep_square: Square | None = None    # En passant
        self.move_stack: list = []
        self._legal_moves: LegalMoveWrapper = LegalMoveWrapper(self)
        self.reset()


    def __setitem__(self, square: Square | str, piece: Piece):
        if isinstance(square, str):
            square = Square(square)
        self.board[square_rank_index(square)][square_file_index(square)] = piece

    def __getitem__(self, square: Square | str) -> Piece:
        if isinstance(square, str):
            square = Square(square)
        return self.board[square_rank_index(square)][square_file_index(square)]

    def reset(self):
        for f in range(8):
            self[chr(ord('a') + f) + '2'] = Piece.from_symbol('P')
            self[chr(ord('a') + f) + '7'] = Piece.from_symbol('p')
        self['a1'] = Piece.from_symbol('R')
        self['h1'] = Piece.from_symbol('R')
        self['a8'] = Piece.from_symbol('r')
        self['h8'] = Piece.from_symbol('r')
        self['b1'] = Piece.from_symbol('N')
        self['g1'] = Piece.from_symbol('N')
        self['b8'] = Piece.from_symbol('n')
        self['g8'] = Piece.from_symbol('n')
        self['c1'] = Piece.from_symbol('B')
        self['f1'] = Piece.from_symbol('B')
        self['c8'] = Piece.from_symbol('b')
        self['f8'] = Piece.from_symbol('b')
        self['d1'] = Piece.from_symbol('Q')
        self['e1'] = Piece.from_symbol('K')
        self['d8'] = Piece.from_symbol('q')
        self['e8'] = Piece.from_symbol('k')

        self.turn = Color.WHITE
        self.castling_right = {'K' : True, 'k' : True, 'Q' : True, 'q' : True}     # Castling rights for both players
        self.fullmove_number: int = 1    # Increment by one after each black's turn
        self.halfmove_clock: int = 0     # Counter for 50-move draw rule
        self.ep_square: Square | None = None    # En passant
        self._legal_moves = LegalMoveWrapper(self)
        self.move_stack: list = []

    def can_castle_kingside(self) -> bool:
        if not self.castling_right['K' if self.turn == Color.WHITE else 'k'] or self.is_in_check():
            return False

        for file_index in range(5, 7):
            square = get_square(0 if self.turn == Color.WHITE else 7, file_index)
            if (not self.is_empty_square(square)) or self.is_under_attack(square):
                return False

        return (self.is_empty_square(Square.G1)) if self.turn == Color.WHITE \
            else (self.is_empty_square(Square.G8))

    def can_castle_queenside(self) -> bool:
        if not self.castling_right['Q' if self.turn == Color.WHITE else 'q'] or self.is_in_check():
            return False

        # Check if the squares on the way are not under attack
        for file_index in range(2, 4):
            square = get_square(0 if self.turn == Color.WHITE else 7, file_index)
            if (not self.is_empty_square(square)) or self.is_under_attack(square):
                return False

        return (self.is_empty_square(Square.B1) and self.is_empty_square(Square.C1)) \
                if self.turn == Color.WHITE else (self.is_empty_square(Square.B8) and self.is_empty_square(Square.C8))

    @property
    def legal_moves(self) -> LegalMoveWrapper:
        # Wrapper for generate_legal_moves and is_legal
        # Since legal_moves need to be reset after each turn
        if self._legal_moves.board.fullmove_number != self.fullmove_number or self._legal_moves.board.turn != self.turn:
            # Generate new set of legal moves
            # print("Recalculating legal moves")
            self._legal_moves = LegalMoveWrapper(self)
        return self._legal_moves

    def generate_legal_moves(self) -> List[Move]:
        moves_list = []
        for sq in Square:
            if self[sq].color == self.turn:
                if self[sq].piece_type == PieceType.ROOK:
                    moves_list.extend(self.generate_rook_moves(sq))
                if self[sq].piece_type == PieceType.KNIGHT:
                    moves_list.extend(self.generate_knight_moves(sq))
                if self[sq].piece_type == PieceType.BISHOP:
                    moves_list.extend(self.generate_bishop_moves(sq))
                if self[sq].piece_type == PieceType.QUEEN:
                    moves_list.extend(self.generate_queen_moves(sq))
                if self[sq].piece_type == PieceType.KING:
                    moves_list.extend(self.generate_king_moves(sq))
                if self[sq].piece_type == PieceType.PAWN:
                    moves_list.extend(self.generate_pawn_moves(sq))
        legal_moves_list = []
        for move in moves_list:
            temp_board = deepcopy(self)
            temp_board.perform_move(move)
            temp_board.turn = Color(-temp_board.turn.value)
            if not temp_board.is_in_check():
                legal_moves_list.append(move)
        return legal_moves_list

    def perform_move(self, move: Move):
        if self[move.from_square].piece_type == PieceType.KING and abs(square_file_index(move.from_square) - square_file_index(move.to_square)) == 2:
            # This is a castling move
            if square_file_index(move.to_square) > square_file_index(move.from_square):
                # Kingside castling
                rook_from_square = get_square(square_rank_index(move.from_square), square_file_index(Square.H1))
                rook_to_square = get_square(square_rank_index(move.from_square), square_file_index(Square.F1))
            else:
                # Queenside castling
                rook_from_square = get_square(square_rank_index(move.from_square), square_file_index(Square.A1))
                rook_to_square = get_square(square_rank_index(move.from_square), square_file_index(Square.D1))

                # Move the rook
            self[rook_to_square] = self[rook_from_square]
            self[rook_from_square] = Piece.from_symbol('_')

        self[move.to_square] = self[move.from_square]
        self[move.from_square] = Piece.from_symbol('_')

        self.turn = Color(-self.turn.value)
        if self.turn == Color.WHITE:
            self.fullmove_number += 1

        if self[move.to_square].piece_type == PieceType.PAWN:
            self.halfmove_clock = 0
            if abs(square_rank_index(move.to_square) - square_rank_index(move.from_square)) == 2:
                # If a pawn move is advancing 2 squares, update en passant square
                if self[move.to_square].color == Color.WHITE:
                    self.ep_square = Square(move.to_square.value[0] + '3')
                else:
                    self.ep_square = Square(move.to_square.value[0] + '6')
            else:
                if move.to_square == self.ep_square:
                    ep_rank = square_rank_index(self.ep_square)
                    ep_file = square_file_index(self.ep_square)
                    self[get_square(ep_rank + self.turn.value, ep_file)] = Piece.from_symbol('_')
                self.ep_square = None
        else:
            self.halfmove_clock += 1
            self.ep_square = None

        if move.from_square == Square.A1:
            self.castling_right['Q'] = False
        if move.from_square == Square.H1:
            self.castling_right['K'] = False
        if move.from_square == Square.A8:
            self.castling_right['q'] = False
        if move.from_square == Square.H8:
            self.castling_right['k'] = False
        if move.from_square == Square.E1:
            self.castling_right['K'] = False
            self.castling_right['Q'] = False
        if move.from_square == Square.E8:
            self.castling_right['k'] = False
            self.castling_right['q'] = False

        self.move_stack.append(move)

    def is_empty_square(self, square: Square) -> bool:
        # Check if the square is empty
        return self[square].piece_type == PieceType.EMPTY

    def generate_rook_moves(self, square: Square) -> List[Move]:
        rook_moves = []
        rank = square_rank_index(square)
        file = square_file_index(square)

        # Iterate in four directions: up, down, left, right
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for delta_rank, delta_file in directions:
            target_rank, target_file = rank + delta_rank, file + delta_file

            while is_valid_square(target_rank, target_file):
                target_square = get_square(target_rank, target_file)

                if self.is_empty_square(target_square) or self[square].color != self[target_square].color:
                    rook_moves.append(Move(square, target_square))
                if not self.is_empty_square(target_square):
                    break

                target_rank += delta_rank
                target_file += delta_file

        return rook_moves

    def generate_knight_moves(self, square: Square) -> List[Move]:
        knight_moves = []

        # Extract rank and file indices from the given square
        rank = square_rank_index(square)
        file = square_file_index(square)

        # Iterate over all possible knight moves
        knight_move_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for offset_rank, offset_file in knight_move_offsets:
            target_rank = rank + offset_rank
            target_file = file + offset_file

            if is_valid_square(target_rank, target_file):
                target_square = get_square(target_rank, target_file)
                if self[square].color != self[target_square].color or self.is_empty_square(target_square):
                    knight_moves.append(Move(square, target_square))

        return knight_moves

    def generate_bishop_moves(self, square: Square) -> List[Move]:
        bishop_moves = []
        # Extract rank and file indices from the given square
        rank = square_rank_index(square)
        file = square_file_index(square)

        # Iterate diagonally outward from the current square
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for delta_rank, delta_file in directions:
            target_rank, target_file = rank + delta_rank, file + delta_file

            while is_valid_square(target_rank, target_file):
                target_square = get_square(target_rank, target_file)

                if self.is_empty_square(target_square) or self[square].color != self[target_square].color:
                    bishop_moves.append(Move(square, target_square))
                if not self.is_empty_square(target_square):
                    break

                target_rank += delta_rank
                target_file += delta_file

        return bishop_moves

    def generate_queen_moves(self, square: Square) -> List[Move]:
        queen_moves = []

        # Combine movements of rook and bishop
        queen_moves.extend(self.generate_rook_moves(square))
        queen_moves.extend(self.generate_bishop_moves(square))

        return queen_moves

    def generate_king_moves(self, square: Square) -> List[Move]:
        king_moves = []
        # Extract rank and file indices from the given square
        rank = square_rank_index(square)
        file = square_file_index(square)
        # Iterate over all adjacent squares
        for delta_rank in range(-1, 2):
            for delta_file in range(-1, 2):
                target_rank, target_file = rank + delta_rank, file + delta_file

                # Skip the current square
                if delta_rank == 0 and delta_file == 0:
                    continue

                if is_valid_square(target_rank, target_file):
                    target_square = get_square(target_rank, target_file)

                    if not self[square].color == self[target_square].color or self.is_empty_square(target_square):
                        king_moves.append(Move(square, target_square))

        if self.can_castle_kingside():
            kingside_square = get_square(rank, file + 2)
            king_moves.append(Move(square, kingside_square))

        if self.can_castle_queenside():
            queenside_square = get_square(rank, file - 2)
            king_moves.append(Move(square, queenside_square))

        return king_moves

    def generate_pawn_moves(self, square: Square) -> List[Move]:
        pawn_moves = []

        # Extract rank and file indices from the given square
        rank = square_rank_index(square)
        file = square_file_index(square)

        # Determine the direction of pawn movement based on color
        direction = 1 if self.turn == Color.WHITE else -1

        # Pawn single move
        target_rank = rank + direction
        target_file = file

        if is_valid_square(target_rank, target_file) and self.is_empty_square(get_square(target_rank, target_file)):

            if (self.turn == Color.WHITE and rank == 6) or (self.turn == Color.BLACK and rank == 1):
                # Add promotion moves for each possible promoted piece
                for piece_type in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                    pawn_moves.append(Move(square, get_square(target_rank, target_file), promotion=piece_type))
            else:
                pawn_moves.append(Move(square, get_square(target_rank, target_file)))

        # Pawn double move from starting rank
        if (
                ((self.turn == Color.WHITE and rank == 1) or (self.turn == Color.BLACK and rank == 6))
                and self.is_empty_square(get_square(target_rank, target_file))
                and self.is_empty_square(get_square(target_rank + direction, target_file))
        ):
            pawn_moves.append(Move(square, get_square(target_rank + direction, target_file)))

        # Pawn captures diagonally
        capture_offsets = [(direction, -1), (direction, 1)]
        for offset_rank, offset_file in capture_offsets:
            target_rank = rank + offset_rank
            target_file = file + offset_file
            if (is_valid_square(target_rank, target_file) and not self.is_empty_square(get_square(target_rank, target_file)) and \
                    not self[square].color == self[get_square(target_rank, target_file)].color):
                if (self.turn == Color.WHITE and rank == 6) or (self.turn == Color.BLACK and rank == 1):
                    # Add promotion moves for each possible promoted piece
                    for piece_type in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                        pawn_moves.append(Move(square, get_square(target_rank, target_file), promotion=piece_type))
                else:
                    pawn_moves.append(Move(square, get_square(target_rank, target_file)))

        if self.ep_square is not None:
            ep_rank = square_rank_index(self.ep_square)
            ep_file = square_file_index(self.ep_square)

            if ep_rank == rank and abs(ep_file - file) == 1:
                pawn_moves.append(Move(square, self.ep_square))

        return pawn_moves

    def is_under_attack(self, square: Square) -> bool:
        # Check if the square is under attack by the opponent
        opponent_color = Color.WHITE if self.turn == Color.BLACK else Color.BLACK

        # Iterate over all opponent's pieces and check if they can attack the square
        for from_rank in range(8):
            for from_file in range(8):
                piece = self.board[from_rank][from_file]

                # Skip empty squares or squares with the same-color pieces
                if piece.piece_type == PieceType.EMPTY or piece.color == self.turn:
                    continue

                # Check if the opponent's piece can attack the target square
                if piece.piece_type == PieceType.PAWN:
                    # Pawn attacks
                    direction = 1 if piece.color == Color.WHITE else -1
                    capture_offsets = [(direction, -1), (direction, 1)]
                    for offset_rank, offset_file in capture_offsets:
                        target_rank = from_rank + offset_rank
                        target_file = from_file + offset_file
                        if is_valid_square(target_rank, target_file) and square == get_square(target_rank, target_file):
                            return True

                elif piece.piece_type == PieceType.KNIGHT:
                    # Knight attacks
                    knight_move_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
                    for offset_rank, offset_file in knight_move_offsets:
                        target_rank = from_rank + offset_rank
                        target_file = from_file + offset_file
                        if is_valid_square(target_rank, target_file) and square == get_square(target_rank, target_file):
                            return True

                elif piece.piece_type == PieceType.BISHOP:
                    # Bishop attacks
                    for offset_rank, offset_file in zip([-1, -1, 1, 1], [-1, 1, -1, 1]):
                        target_rank, target_file = from_rank + offset_rank, from_file + offset_file
                        while is_valid_square(target_rank, target_file):
                            if square == get_square(target_rank, target_file):
                                return True
                            if not self.is_empty_square(get_square(target_rank, target_file)):
                                break
                            target_rank += offset_rank
                            target_file += offset_file

                elif piece.piece_type == PieceType.ROOK:
                    # Rook attacks
                    for offset_rank, offset_file in zip([-1, 0, 1, 0], [0, 1, 0, -1]):
                        target_rank, target_file = from_rank + offset_rank, from_file + offset_file
                        while is_valid_square(target_rank, target_file):
                            if square == get_square(target_rank, target_file):
                                return True
                            if not self.is_empty_square(get_square(target_rank, target_file)):
                                break
                            target_rank += offset_rank
                            target_file += offset_file

                elif piece.piece_type == PieceType.QUEEN:
                    # Queen attacks (combination of rook and bishop)
                    for offset_rank, offset_file in zip([-1, -1, 1, 1, -1, 0, 1, 0], [-1, 1, -1, 1, 0, 1, 0, -1]):
                        target_rank, target_file = from_rank + offset_rank, from_file + offset_file
                        while is_valid_square(target_rank, target_file):
                            if square == get_square(target_rank, target_file):
                                return True
                            if not self.is_empty_square(get_square(target_rank, target_file)):
                                break
                            target_rank += offset_rank
                            target_file += offset_file

                elif piece.piece_type == PieceType.KING:
                    # King attacks
                    for offset_rank, offset_file in zip([-1, -1, -1, 0, 1, 1, 1, 0], [-1, 0, 1, 1, 1, 0, -1, -1]):
                        target_rank, target_file = from_rank + offset_rank, from_file + offset_file
                        if is_valid_square(target_rank, target_file) and square == get_square(target_rank, target_file):
                            return True
        return False


    def is_in_check(self) -> bool:
        # Return true if the current player is checking the opponent
        king_pos = None
        for sq in Square:
            if self[sq] == Piece(PieceType.KING, self.turn):
                king_pos = sq
                break
        for sq in Square:
            if self[sq].piece_type != PieceType.EMPTY and self[sq].color != self.turn:
                if self.is_under_attack(king_pos):
                    return True
        return False

    def is_legal(self, move: Move):
        return move in self.legal_moves

    def is_stalemate(self):
        return len(self.legal_moves) == 0 and not self.is_in_check()

    def is_checkmate(self):
        return len(self.legal_moves) == 0 and self.is_in_check()

    def insufficient_material(self) -> bool:
        def count_material(color):
            return sum(self[square].piece_type != PieceType.EMPTY and self[square].color == color for square in Square)

        white_material, black_material = count_material(Color.WHITE), count_material(Color.BLACK)

        return white_material == black_material == 1 or (
                white_material <= 2 and not any(self[square].piece_type != PieceType.PAWN and self[square].color == Color.WHITE for square in Square)
        ) or (
                black_material <= 2 and not any(self[square].piece_type != PieceType.PAWN and self[square].color == Color.BLACK for square in Square)
        )

    def is_terminated(self):
        return self.is_checkmate() or self.is_stalemate() or self.halfmove_clock == 50 or self.insufficient_material()

    def push(self, move: Move):
        if self.is_terminated():
            raise GameTerminatedError("Game is already terminated")
        if self.is_legal(move):
            self.perform_move(move)
        else:
            raise IllegalMoveError(f"Move {move} is illegal")

    def __str__(self):
        return '\n'.join([' '.join([str(self[get_square(x, y)]) for y in range(8)]) for x in range(7,-1,-1)])

#
# board = Board()
# # while not board.is_terminated():
# for move in "e2e4 e7e5 f1c4 f8c5 d1h5 d7d6 b1c3 a7a5 g1f3 a5a4 e1g1 h7h6 b2b4 a4b3 h5f7 ".split():
#     print(board.legal_moves)
#     print(board.castling_right)
#     print(board.turn)
#     print(board.ep_square)
#     print(board.move_stack)
#     print(board.can_castle_kingside())
#     print(board)
#     # move = input("Enter your move (UCI): ")
#     board.push(Move.from_uci(move))
#

#e2e4 e7e5 f1c4 f8c5 d1h5 d7d6 b1c3 a7a5 g1f3 a5a4 e1g1 h7h6 b2b4 a4b3 a6a5 h5f7