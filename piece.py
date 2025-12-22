import pygame
from enum import Enum
import os

class PieceColor(Enum):
    WHITE = "white"
    BLACK = "black"
    
class PieceType(Enum):
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"

class Piece:
    def __init__(self, piece_type, color):
        self.type = piece_type
        self.color = color
        self.has_moved = False
        self.image = self.load_image()
    
    def load_image(self):
        filename = f"{self.color.value}_{self.type.value}.png"
        path = os.path.join("images", filename)
        image = pygame.image.load(path)
        size = (75, 75) if self.type == PieceType.PAWN else (90, 90)
        return pygame.transform.scale(image, size)
    
    def draw(self, screen, x, y):
        offset_x = (100 - self.image.get_width()) // 2
        offset_y = (100 - self.image.get_height()) // 2
        screen.blit(self.image, (x + offset_x, y + offset_y))
    
    def __repr__(self):
        return f"{self.color.value}_{self.type.value}"