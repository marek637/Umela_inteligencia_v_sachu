from piece import Piece, PieceType, PieceColor

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.setup_pieces()
    
    def setup_pieces(self):
        for col in range(8):
            self.grid[1][col] = Piece(PieceType.PAWN, PieceColor.BLACK)
            self.grid[6][col] = Piece(PieceType.PAWN, PieceColor.WHITE)
        
        self.grid[0][0] = Piece(PieceType.ROOK, PieceColor.BLACK)
        self.grid[0][1] = Piece(PieceType.KNIGHT, PieceColor.BLACK)
        self.grid[0][2] = Piece(PieceType.BISHOP, PieceColor.BLACK)
        self.grid[0][3] = Piece(PieceType.QUEEN, PieceColor.BLACK)
        self.grid[0][4] = Piece(PieceType.KING, PieceColor.BLACK)
        self.grid[0][5] = Piece(PieceType.BISHOP, PieceColor.BLACK)
        self.grid[0][6] = Piece(PieceType.KNIGHT, PieceColor.BLACK)
        self.grid[0][7] = Piece(PieceType.ROOK, PieceColor.BLACK)
        
        self.grid[7][0] = Piece(PieceType.ROOK, PieceColor.WHITE)
        self.grid[7][1] = Piece(PieceType.KNIGHT, PieceColor.WHITE)
        self.grid[7][2] = Piece(PieceType.BISHOP, PieceColor.WHITE)
        self.grid[7][3] = Piece(PieceType.QUEEN, PieceColor.WHITE)
        self.grid[7][4] = Piece(PieceType.KING, PieceColor.WHITE)
        self.grid[7][5] = Piece(PieceType.BISHOP, PieceColor.WHITE)
        self.grid[7][6] = Piece(PieceType.KNIGHT, PieceColor.WHITE)
        self.grid[7][7] = Piece(PieceType.ROOK, PieceColor.WHITE)
    
    def get_piece(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        if 0 <= row < 8 and 0 <= col < 8:
            self.grid[row][col] = piece
    
    def move_piece(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.get_piece(from_row, from_col)
        if piece:
            piece.has_moved = True
            self.set_piece(to_row, to_col, piece)
            self.set_piece(from_row, from_col, None)
            return True
        return False
    
    def is_empty(self, row, col):
        return self.get_piece(row, col) is None
    
    def is_valid_position(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8