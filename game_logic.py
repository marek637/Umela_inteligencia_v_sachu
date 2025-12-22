from piece import PieceType, PieceColor

class GameLogic:
    def __init__(self, board):
        self.board = board
        self.current_turn = PieceColor.WHITE
        self.last_move = None
        self.en_passant_target = None
    
    def get_valid_moves(self, row, col):
        piece = self.board.get_piece(row, col)
        if not piece:
            return []
        
        moves = []
        
        if piece.type == PieceType.PAWN:
            moves = self.get_pawn_moves(row, col, piece)
        elif piece.type == PieceType.ROOK:
            moves = self.get_rook_moves(row, col, piece)
        elif piece.type == PieceType.KNIGHT:
            moves = self.get_knight_moves(row, col, piece)
        elif piece.type == PieceType.BISHOP:
            moves = self.get_bishop_moves(row, col, piece)
        elif piece.type == PieceType.QUEEN:
            moves = self.get_queen_moves(row, col, piece)
        elif piece.type == PieceType.KING:
            moves = self.get_king_moves(row, col, piece)
        
        return moves
    
    def get_pawn_moves(self, row, col, piece):
        moves = []
        direction = -1 if piece.color == PieceColor.WHITE else 1
        
        new_row = row + direction
        if self.board.is_valid_position(new_row, col) and self.board.is_empty(new_row, col):
            moves.append((new_row, col))
            
            if not piece.has_moved:
                new_row2 = row + 2 * direction
                if self.board.is_empty(new_row2, col):
                    moves.append((new_row2, col))
        
        for dcol in [-1, 1]:
            new_row = row + direction
            new_col = col + dcol
            if self.board.is_valid_position(new_row, new_col):
                target = self.board.get_piece(new_row, new_col)
                if target and target.color != piece.color:
                    moves.append((new_row, new_col))
        
        if self.en_passant_target:
            ep_row, ep_col = self.en_passant_target
            new_row = row + direction
            for dcol in [-1, 1]:
                new_col = col + dcol
                if (new_row, new_col) == (ep_row, ep_col):
                    moves.append((new_row, new_col))
        
        return moves
    
    def get_rook_moves(self, row, col, piece):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.board.is_valid_position(new_row, new_col):
                    break
                
                target = self.board.get_piece(new_row, new_col)
                if target:
                    if target.color != piece.color:
                        moves.append((new_row, new_col))
                    break
                else:
                    moves.append((new_row, new_col))
        
        return moves
    
    def get_knight_moves(self, row, col, piece):
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.board.is_valid_position(new_row, new_col):
                target = self.board.get_piece(new_row, new_col)
                if not target or target.color != piece.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def get_bishop_moves(self, row, col, piece):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not self.board.is_valid_position(new_row, new_col):
                    break
                
                target = self.board.get_piece(new_row, new_col)
                if target:
                    if target.color != piece.color:
                        moves.append((new_row, new_col))
                    break
                else:
                    moves.append((new_row, new_col))
        
        return moves
    
    def get_queen_moves(self, row, col, piece):
        return self.get_rook_moves(row, col, piece) + self.get_bishop_moves(row, col, piece)
    
    def get_king_moves(self, row, col, piece):
        moves = []
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                     (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in king_moves:
            new_row, new_col = row + dr, col + dc
            if self.board.is_valid_position(new_row, new_col):
                target = self.board.get_piece(new_row, new_col)
                if not target or target.color != piece.color:
                    if not self.is_square_attacked_by_opponent(new_row, new_col, piece.color):
                        moves.append((new_row, new_col))
        
        if not piece.has_moved:
            if self.can_castle_kingside(row, col, piece):
                moves.append((row, col + 2))
            
            if self.can_castle_queenside(row, col, piece):
                moves.append((row, col - 2))
        
        return moves
    
    def is_square_attacked_by_opponent(self, row, col, color):
        opponent_color = PieceColor.BLACK if color == PieceColor.WHITE else PieceColor.WHITE
        
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece and piece.color == opponent_color:
                    if piece.type == PieceType.PAWN:
                        direction = -1 if piece.color == PieceColor.WHITE else 1
                        for dcol in [-1, 1]:
                            if r + direction == row and c + dcol == col:
                                return True
                    elif piece.type == PieceType.KNIGHT:
                        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                                      (1, -2), (1, 2), (2, -1), (2, 1)]
                        for dr, dc in knight_moves:
                            if r + dr == row and c + dc == col:
                                return True
                    else:
                        if piece.type in [PieceType.ROOK, PieceType.QUEEN]:
                            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                            for dr, dc in directions:
                                for i in range(1, 8):
                                    check_r, check_c = r + dr * i, c + dc * i
                                    if not self.board.is_valid_position(check_r, check_c):
                                        break
                                    if check_r == row and check_c == col:
                                        return True
                                    if self.board.get_piece(check_r, check_c):
                                        break
                        
                        if piece.type in [PieceType.BISHOP, PieceType.QUEEN]:
                            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                            for dr, dc in directions:
                                for i in range(1, 8):
                                    check_r, check_c = r + dr * i, c + dc * i
                                    if not self.board.is_valid_position(check_r, check_c):
                                        break
                                    if check_r == row and check_c == col:
                                        return True
                                    if self.board.get_piece(check_r, check_c):
                                        break
                        
                        if piece.type == PieceType.KING:
                            king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                                        (0, 1), (1, -1), (1, 0), (1, 1)]
                            for dr, dc in king_moves:
                                if r + dr == row and c + dc == col:
                                    return True
        
        return False
    
    def can_castle_kingside(self, row, col, king):
        rook = self.board.get_piece(row, 7)
        if not rook or rook.type != PieceType.ROOK or rook.has_moved:
            return False
        
        if not self.board.is_empty(row, 5) or not self.board.is_empty(row, 6):
            return False
        
        if self.is_square_attacked_by_opponent(row, col, king.color):
            return False
        
        if self.is_square_attacked_by_opponent(row, col + 1, king.color):
            return False
        
        if self.is_square_attacked_by_opponent(row, col + 2, king.color):
            return False
        
        return True
    
    def can_castle_queenside(self, row, col, king):
        rook = self.board.get_piece(row, 0)
        if not rook or rook.type != PieceType.ROOK or rook.has_moved:
            return False
        
        if not self.board.is_empty(row, 1) or not self.board.is_empty(row, 2) or not self.board.is_empty(row, 3):
            return False
        
        if self.is_square_attacked_by_opponent(row, col, king.color):
            return False
        
        if self.is_square_attacked_by_opponent(row, col - 1, king.color):
            return False
        
        if self.is_square_attacked_by_opponent(row, col - 2, king.color):
            return False
        
        return True
    
    def move_piece(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board.get_piece(from_row, from_col)
        if not piece:
            return False
        
        if piece.type == PieceType.PAWN and self.en_passant_target:
            if (to_row, to_col) == self.en_passant_target:
                if piece.color == PieceColor.WHITE:
                    captured_pawn_row = to_row + 1
                else:
                    captured_pawn_row = to_row - 1
                
                self.board.set_piece(captured_pawn_row, to_col, None)
        
        if piece.type == PieceType.KING and abs(to_col - from_col) == 2:
            if to_col > from_col:
                rook = self.board.get_piece(from_row, 7)
                if rook:
                    self.board.set_piece(from_row, 5, rook)
                    self.board.set_piece(from_row, 7, None)
                    rook.has_moved = True
            else:
                rook = self.board.get_piece(from_row, 0)
                if rook:
                    self.board.set_piece(from_row, 3, rook)
                    self.board.set_piece(from_row, 0, None)
                    rook.has_moved = True
        
        self.board.move_piece(from_pos, to_pos)
        
        self.en_passant_target = None
        if piece.type == PieceType.PAWN and abs(to_row - from_row) == 2:
            if piece.color == PieceColor.WHITE:
                self.en_passant_target = (to_row + 1, to_col)
            else:
                self.en_passant_target = (to_row - 1, to_col)
        
        self.last_move = (from_pos, to_pos)
        
        self.current_turn = PieceColor.BLACK if self.current_turn == PieceColor.WHITE else PieceColor.WHITE
        
        return True
