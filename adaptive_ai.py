from piece import PieceType, PieceColor
import copy
import random
import json
import os
from datetime import datetime
class PlayerProfile:
    
    def __init__(self, filename="player_profile.json"):
        self.filename = filename
        self.games_played = 0
        self.moves_history = []
        self.opening_moves = {}
        self.piece_preferences = {
            PieceType.PAWN.value: 0,
            PieceType.KNIGHT.value: 0,
            PieceType.BISHOP.value: 0,
            PieceType.ROOK.value: 0,
            PieceType.QUEEN.value: 0,
            PieceType.KING.value: 0
        }
        self.average_thinking_time = 2.0
        self.mistake_rate = 0.3
        self.aggression_level = 0.5
        self.wins = 0
        self.losses = 0
        self.load_profile()
    
    def load_profile(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.games_played = data.get('games_played', 0)
                    self.moves_history = data.get('moves_history', [])
                    self.piece_preferences = data.get('piece_preferences', self.piece_preferences)
                    self.average_thinking_time = data.get('average_thinking_time', 2.0)
                    # normalize mistake rate to a fraction 0..1
                    loaded_rate = data.get('mistake_rate', 0.3)
                    try:
                        r = float(loaded_rate)
                    except (TypeError, ValueError):
                        r = 0.3
                    if r > 1.0:  # was stored as percentage like 30.0
                        r = r / 100.0
                    self.mistake_rate = max(0.0, min(1.0, r))
                    self.aggression_level = data.get('aggression_level', 0.5)
                    self.wins = data.get('wins', 0)
                    self.losses = data.get('losses', 0)
                    self.opening_moves = data.get('opening_moves', {})
            except Exception as e:
                print(f"⚠ Chyba pri načítaní profilu: {e}, vytváram nový")
    
    def save_profile(self):
        data = {
            'games_played': self.games_played,
            'moves_history': self.moves_history[-1000:],
            'piece_preferences': self.piece_preferences,
            'average_thinking_time': self.average_thinking_time,
            'mistake_rate': round(max(0.0, min(1.0, self.mistake_rate)), 4),
            'aggression_level': self.aggression_level,
            'wins': self.wins,
            'losses': self.losses,
            'opening_moves': self.opening_moves,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def record_move(self, from_pos, to_pos, piece_type, was_capture, move_number):
        move_data = {
            'from': from_pos,
            'to': to_pos,
            'piece': piece_type.value,
            'capture': was_capture,
            'move_num': move_number
        }
        
        self.moves_history.append(move_data)
        self.piece_preferences[piece_type.value] += 1
        
        if move_number <= 5:
            key = f"move_{move_number}"
            if key not in self.opening_moves:
                self.opening_moves[key] = {}
            
            move_key = f"{from_pos}->{to_pos}"
            self.opening_moves[key][move_key] = self.opening_moves[key].get(move_key, 0) + 1
        
        if was_capture:
            self.aggression_level = min(1.0, self.aggression_level + 0.01)
        else:
            self.aggression_level = max(0.0, self.aggression_level - 0.005)
    
    def analyze_skill_level(self):
        if len(self.moves_history) < 20:
            return 1
        
        if self.games_played > 50:
            return 4
        elif self.games_played > 20:
            return 3
        elif self.games_played > 5:
            return 2
        else:
            return 1
    
    def get_estimated_depth(self):
        skill = self.analyze_skill_level()
        return min(3, max(2, skill))
class OptimizedAdaptiveAI:
    
    MAX_TT_SIZE = 10000
    
    def __init__(self, color, player_profile):
        self.color = color
        self.opponent_color = PieceColor.WHITE if color == PieceColor.BLACK else PieceColor.BLACK
        self.profile = player_profile
        self.nodes_searched = 0
        
        self._piece_values = {
            PieceType.PAWN: 100,
            PieceType.KNIGHT: 320,
            PieceType.BISHOP: 330,
            PieceType.ROOK: 500,
            PieceType.QUEEN: 900,
            PieceType.KING: 20000
        }
        
        self.transposition_table = {}
        self.killer_moves = [[None, None] for _ in range(6)]
        self.history_table = {}
        
        self.CENTER_SQUARES = frozenset([(3, 3), (3, 4), (4, 3), (4, 4)])
        self.CENTER_BONUS = 30
    
    def clear_search_data(self):
        if len(self.transposition_table) > self.MAX_TT_SIZE:
            self.transposition_table.clear()
        self.killer_moves = [[None, None] for _ in range(6)]
    
    def get_board_hash(self, board):
        h = 0
        for row in range(8):
            for col in range(8):
                piece = board.grid[row][col]
                if piece:
                    h = hash((h, piece.color.value, piece.type.value, row, col))
        return h
    
    def get_move(self, board, game_logic):
        self.nodes_searched = 0
        self.clear_search_data()
        
        target_depth = self.profile.get_estimated_depth()
        best_move = None
        
        for depth in range(1, target_depth + 1):
            _, move = self.minimax(board, game_logic, depth, -999999, 999999, True, 0)
            if move:
                best_move = move
        
        all_moves = list(self.get_all_moves(board, game_logic, self.color))
        
        if random.random() < self.profile.mistake_rate and len(all_moves) > 1:
            if all_moves:
                if best_move in all_moves:
                    all_moves.remove(best_move)
                if all_moves:
                    best_move = random.choice(all_moves)
                    print(" AI urobilo suboptimálny ťah")
        
        print(f"Optimalizovaná AI (hĺbka {target_depth}): {self.nodes_searched} pozícií")
        return best_move
    
    def get_all_moves(self, board, game_logic, color):
        for row in range(8):
            for col in range(8):
                piece = board.grid[row][col]
                if piece and piece.color == color:
                    moves = game_logic.get_valid_moves(row, col)
                    for to_row, to_col in moves:
                        yield ((row, col), (to_row, to_col))
    
    def order_moves(self, board, game_logic, color, ply):
        
        captures = []
        quiet = []
        opponent = self.opponent_color if color == self.color else self.color
        
        for row in range(8):
            for col in range(8):
                piece = board.grid[row][col]
                if not piece or piece.color != color:
                    continue
                
                from_pos = (row, col)
                piece_value = self._piece_values[piece.type]
                valid_moves = game_logic.get_valid_moves(row, col)
                
                for to_row, to_col in valid_moves:
                    to_pos = (to_row, to_col)
                    target = board.grid[to_row][to_col]
                    move = (from_pos, to_pos)
                    
                    if target and target.color == opponent:
                        score = self._piece_values[target.type] * 10 - piece_value
                        captures.append((score, from_pos, to_pos))
                    else:
                        score = 0
                        if ply < len(self.killer_moves) and move in self.killer_moves[ply]:
                            score += 1000
                        if to_pos in self.CENTER_SQUARES:
                            score += 50
                        quiet.append((score, from_pos, to_pos))
        
        captures.sort(reverse=True)
        quiet.sort(reverse=True)
        
        for _, from_pos, to_pos in captures:
            yield from_pos, to_pos
        for _, from_pos, to_pos in quiet:
            yield from_pos, to_pos
    
    def minimax(self, board, game_logic, depth, alpha, beta, is_maximizing, ply):
        self.nodes_searched += 1
        
        board_hash = self.get_board_hash(board)
        if board_hash in self.transposition_table:
            stored_depth, stored_eval, stored_move = self.transposition_table[board_hash]
            if stored_depth >= depth:
                return stored_eval, stored_move
        
        if depth == 0:
            eval_score = self.quiescence_search(board, game_logic, alpha, beta, is_maximizing, 3)
            return eval_score, None
        
        best_move = None
        
        if is_maximizing:
            max_eval = -999999
            move_count = 0
            
            for from_pos, to_pos in self.order_moves(board, game_logic, self.color, ply):
                move_count += 1
                
                game_logic_copy = copy.copy(game_logic)
                game_logic_copy.board = copy.deepcopy(board)
                game_logic_copy.move_piece(from_pos, to_pos)
                
                eval_score, _ = self.minimax(game_logic_copy.board, game_logic_copy,
                                            depth - 1, alpha, beta, False, ply + 1)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (from_pos, to_pos)
                    
                    if ply < len(self.killer_moves):
                        if best_move not in self.killer_moves[ply]:
                            self.killer_moves[ply][1] = self.killer_moves[ply][0]
                            self.killer_moves[ply][0] = best_move
                
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            
            if move_count == 0:
                return -99999, None
            
            if len(self.transposition_table) < self.MAX_TT_SIZE:
                self.transposition_table[board_hash] = (depth, max_eval, best_move)
            
            return max_eval, best_move
        
        else:
            min_eval = 999999
            move_count = 0
            
            for from_pos, to_pos in self.order_moves(board, game_logic, self.opponent_color, ply):
                move_count += 1
                
                game_logic_copy = copy.copy(game_logic)
                game_logic_copy.board = copy.deepcopy(board)
                game_logic_copy.move_piece(from_pos, to_pos)
                
                eval_score, _ = self.minimax(game_logic_copy.board, game_logic_copy,
                                            depth - 1, alpha, beta, True, ply + 1)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (from_pos, to_pos)
                
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            if move_count == 0:
                return 99999, None
            
            if len(self.transposition_table) < self.MAX_TT_SIZE:
                self.transposition_table[board_hash] = (depth, min_eval, best_move)
            
            return min_eval, best_move
    
    def quiescence_search(self, board, game_logic, alpha, beta, is_maximizing, max_depth):
        
        self.nodes_searched += 1
        
        if max_depth <= 0:
            return self.evaluate_position(board)
        
        stand_pat = self.evaluate_position(board)
        
        if is_maximizing:
            if stand_pat >= beta:
                return beta
            if alpha < stand_pat:
                alpha = stand_pat
            
            for from_pos, to_pos in self.get_capture_moves(board, game_logic, self.color):
                game_logic_copy = copy.copy(game_logic)
                game_logic_copy.board = copy.deepcopy(board)
                game_logic_copy.move_piece(from_pos, to_pos)
                
                score = self.quiescence_search(game_logic_copy.board, game_logic_copy, 
                                              alpha, beta, False, max_depth - 1)
                
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
            
            return alpha
        else:
            if stand_pat <= alpha:
                return alpha
            if beta > stand_pat:
                beta = stand_pat
            
            for from_pos, to_pos in self.get_capture_moves(board, game_logic, self.opponent_color):
                game_logic_copy = copy.copy(game_logic)
                game_logic_copy.board = copy.deepcopy(board)
                game_logic_copy.move_piece(from_pos, to_pos)
                
                score = self.quiescence_search(game_logic_copy.board, game_logic_copy, 
                                              alpha, beta, True, max_depth - 1)
                
                if score <= alpha:
                    return alpha
                if score < beta:
                    beta = score
            
            return beta
    
    def get_capture_moves(self, board, game_logic, color):
        opponent = self.opponent_color if color == self.color else self.color
        
        for row in range(8):
            for col in range(8):
                piece = board.grid[row][col]
                if piece and piece.color == color:
                    moves = game_logic.get_valid_moves(row, col)
                    for to_row, to_col in moves:
                        target = board.grid[to_row][to_col]
                        if target and target.color == opponent:
                            yield ((row, col), (to_row, to_col))
    
    def evaluate_position(self, board):
        score = 0
        
        for row in range(8):
            row_pieces = board.grid[row]
            for col in range(8):
                piece = row_pieces[col]
                if not piece:
                    continue
                
                value = self._piece_values[piece.type]
                
                if (row, col) in self.CENTER_SQUARES:
                    value += self.CENTER_BONUS
                
                if piece.type in [PieceType.QUEEN, PieceType.ROOK]:
                    value = int(value * (1 + self.profile.aggression_level * 0.2))
                
                if piece.color == self.color:
                    score += value
                else:
                    score -= value
        
        return score