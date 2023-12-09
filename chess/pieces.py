import chess

from dataclasses import dataclass
from typing import Self

from constants import *

@dataclass
class Piece:
    piece_type: PieceType
    color: Color

    def symbol(self):
        symbol = piece_symbol(self.piece_type)
        return symbol.upper() if self.color == Color.WHITE else symbol

    @classmethod
    def from_symbol(cls, symbol: str) -> Self:
        if symbol == 0:
            return cls(PieceType.EMPTY, Color.EMPTY)
        return cls(PieceType(symbol.lower()), Color.WHITE if symbol.isupper() else Color.BLACK)

    def __str__(self):
        return self.symbol()

    def __hash__(self):
        return self.symbol().__hash__()