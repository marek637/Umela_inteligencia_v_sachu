from piece import PieceType, PieceColor
import copy
import random
AI_DEPTH = 2
RANDOMNESS = 15
PIECE_VALUES = {
    PieceType.PAWN: 100,
    PieceType.KNIGHT: 320,
    PieceType.BISHOP: 330,
    PieceType.ROOK: 500,
    PieceType.QUEEN: 900,
    PieceType.KING: 20000
}
CENTER_BONUS = 30
CENTER_SQUARES = frozenset([(3, 3), (3, 4), (4, 3), (4, 4)])
class AIPlayer:
    
    def __init__(self, color):
        self.color = color
        self.opponent_color = PieceColor.WHITE if color == PieceColor.BLACK else PieceColor.BLACK
        self.nodes_searched = 0
        
        self._piece_values = PIECE_VALUES
    
    def get_move(self, board, game_logic):
        self.nodes_searched = 0
        _, best_move = self.minimax(board, game_logic, AI_DEPTH, -999999, 999999, True)
        print(f"AI: {self.nodes_searched} pozícií")
        return best_move
    
    def get_moves_ordered(self, board, game_logic, color):
      
        captures = []
        quiet_moves = []
        opponent = self.opponent_color if color == self.color else self.color
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if not piece or piece.color != color:
                    continue
                
                from_pos = (row, col)
                piece_value = self._piece_values[piece.type]
                moves = game_logic.get_valid_moves(row, col)
                
                for to_row, to_col in moves:
                    to_pos = (to_row, to_col)
                    target = board.get_piece(to_row, to_col)
                    
                    if target and target.color == opponent:
                        capture_score = self._piece_values[target.type] * 10 - piece_value
                        capture_score += random.randint(-RANDOMNESS, RANDOMNESS)
                        captures.append((capture_score, from_pos, to_pos))
                    else:
                        score = CENTER_BONUS if to_pos in CENTER_SQUARES else 0
                        score += random.randint(-RANDOMNESS, RANDOMNESS)
                        quiet_moves.append((score, from_pos, to_pos))
        
        captures.sort(reverse=True)
        quiet_moves.sort(reverse=True)
        
        for score, from_pos, to_pos in captures:
            yield from_pos, to_pos
        for score, from_pos, to_pos in quiet_moves:
            yield from_pos, to_pos
    def minimax(self, board, game_logic, depth, alpha, beta, is_maximizing):
        self.nodes_searched += 1
        
        if depth == 0:
            return self.evaluate_fast(board), None
        
        best_move = None
        
        if is_maximizing:
            max_eval = -999999
            
            best_moves = []
            
            move_count = 0
            for from_pos, to_pos in self.get_moves_ordered(board, game_logic, self.color):
                move_count += 1
                
                game_logic_copy = copy.copy(game_logic)
                game_logic_copy.board = copy.deepcopy(board)
                game_logic_copy.move_piece(from_pos, to_pos)
                
                eval_score, _ = self.minimax(game_logic_copy.board, game_logic_copy, 
                                            depth - 1, alpha, beta, False)
                
                if depth == AI_DEPTH:
                    eval_score += random.randint(-RANDOMNESS//2, RANDOMNESS//2)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_moves = [(eval_score, (from_pos, to_pos))]
                elif eval_score == max_eval:
                    best_moves.append((eval_score, (from_pos, to_pos)))
                
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            
            if move_count == 0:
                return -99999, None
            
            if best_moves:
                _, best_move = random.choice(best_moves)
                
            return max_eval, best_move
        
        else:
            min_eval = 999999
            best_moves = []
            
            move_count = 0
            for from_pos, to_pos in self.get_moves_ordered(board, game_logic, self.opponent_color):
                move_count += 1
                
                game_logic_copy = copy.copy(game_logic)
                game_logic_copy.board = copy.deepcopy(board)
                game_logic_copy.move_piece(from_pos, to_pos)
                
                eval_score, _ = self.minimax(game_logic_copy.board, game_logic_copy,
                                            depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_moves = [(eval_score, (from_pos, to_pos))]
                elif eval_score == min_eval:
                    best_moves.append((eval_score, (from_pos, to_pos)))
                
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            if move_count == 0:
                return 99999, None
            
            if best_moves:
                _, best_move = random.choice(best_moves)
                
            return min_eval, best_move
    
    def evaluate_fast(self, board):
        score = 0
        
        for row in range(8):
            row_pieces = board.grid[row]
            for col in range(8):
                piece = row_pieces[col]
                if not piece:
                    continue
                
                value = self._piece_values[piece.type]
                
                if piece.color == self.color:
                    score += value
                    if (row, col) in CENTER_SQUARES:
                        score += CENTER_BONUS
                else:
                    score -= value
                    if (row, col) in CENTER_SQUARES:
                        score -= CENTER_BONUS
        
        return score
