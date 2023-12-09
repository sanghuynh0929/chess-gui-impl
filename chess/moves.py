from typing import Optional, Self
from dataclasses import dataclass

from constants import *
from errors import *


@dataclass
class Move:
    from_square: Square
    to_square: Square
    promotion: Optional[PieceType] = None

    def uci(self) -> str:
        # Example: 'e2e4' for pawn e2 -> e4
        return self.from_square.value + self.to_square.value

    def __str__(self):
        return self.uci()
    def __repr__(self):
        return self.__str__()
    @classmethod
    def from_uci(cls, uci) -> Self:
        if 4 <= len(uci) <= 5:
            try:
                from_square = Square(uci[0:2])
                to_square = Square(uci[2:4])
                promotion = PieceType(uci[4]) if len(uci) == 5 else None
            except ValueError:
                raise InvalidMoveError("Invalid UCI")
            if from_square == to_square:
                raise InvalidMoveError("Null move")
            return cls(from_square, to_square, promotion=promotion)
        else:
            raise InvalidMoveError("Improper UCI")

