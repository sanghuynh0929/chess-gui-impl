from enum import Enum
from typing import Self


class Color(Enum):
    WHITE = 1
    BLACK = -1
    EMPTY = 0

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__()


class PieceType(Enum):
    EMPTY = '_'
    PAWN = 'p'
    KNIGHT = 'n'
    BISHOP = 'b'
    ROOK = 'r'
    QUEEN = 'q'
    KING = 'k'

    def __eq__(self, other: Self | str) -> bool:
        if isinstance(other, str):
            return self.value == other
        return self.value == other.value

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return self.value.__hash__()


def piece_symbol(piece_type: PieceType) -> str:
    return piece_type.value


RANK_NAMES = ['1', '2', '3', '4', '5', '6', '7', '8']
FILE_NAMES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

squares = [f + r for r in RANK_NAMES for f in FILE_NAMES]


class Square(Enum):
    A1, B1, C1, D1, E1, F1, G1, H1 = squares[:8]
    A2, B2, C2, D2, E2, F2, G2, H2 = squares[8:16]
    A3, B3, C3, D3, E3, F3, G3, H3 = squares[16:24]
    A4, B4, C4, D4, E4, F4, G4, H4 = squares[24:32]
    A5, B5, C5, D5, E5, F5, G5, H5 = squares[32:40]
    A6, B6, C6, D6, E6, F6, G6, H6 = squares[40:48]
    A7, B7, C7, D7, E7, F7, G7, H7 = squares[48:56]
    A8, B8, C8, D8, E8, F8, G8, H8 = squares[56:]


    def parse_square(cls, name: str) -> Self:
        return Square(name)


    def square_name(self) -> str:
        return self.value



def get_square(rank_index, file_index):
    return Square(FILE_NAMES[file_index] + RANK_NAMES[rank_index])


def is_valid_square(rank, file):
    return 0 <= rank < 8 and 0 <= file < 8


def square_file_index(square: Square):
    return ord(square.value[0]) - ord('a')


def square_rank_index(square: Square):
    return ord(square.value[1]) - ord('1')

