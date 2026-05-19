import pygame
import sys
import os
from board import Board
from piece import Piece, PieceType, PieceColor
from game_logic import GameLogic
from ai_player import AIPlayer
from adaptive_ai import OptimizedAdaptiveAI, PlayerProfile
import copy

pygame.init()

SQUARE_SIZE = 100
BOARD_SIZE = 8
WINDOW_SIZE = SQUARE_SIZE * BOARD_SIZE
CAPTURED_PANEL_WIDTH = 200
BUTTON_HEIGHT = 50
TOTAL_WIDTH = WINDOW_SIZE + CAPTURED_PANEL_WIDTH
TOTAL_HEIGHT = WINDOW_SIZE + BUTTON_HEIGHT
FPS = 60
AI_DELAY = 1000

LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
RED_OUTLINE = (220, 100, 100)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 150, 255)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)
PANEL_BG = (40, 40, 40)
WHITE = (255, 255, 255)


class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
        pygame.display.set_caption("Šach")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.game_logic = GameLogic(self.board)
        self.ai_player = AIPlayer(PieceColor.BLACK)
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []
        self.ai_enabled = False
        self.ai_thinking = False
        self.ai_move_time = 0
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.message_font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)
        self.tiny_font = pygame.font.Font(None, 20)
        self.check_status = None
        self.game_over = False
        self.winner = None
        self.counter = 0
        self.game_started = False
        self.menu_background = self.load_menu_background()
        
        self.promotion_active = False
        self.promotion_pos = None
        self.promotion_color = None
        
        self.captured_white = []
        self.captured_black = []
        
        self.training_mode = False
        self.player_profile = None
        self.adaptive_ai = None
        self.move_number = 0
        
    def load_menu_background(self):
        try:
            image = pygame.image.load("images/menu_image.png")
            return pygame.transform.scale(image, (TOTAL_WIDTH, TOTAL_HEIGHT))
        except:
            return None
    
    def draw_menu(self):
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
            overlay = pygame.Surface((TOTAL_WIDTH, TOTAL_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
        else:
            self.screen.fill((30, 30, 30))
        
        title = self.title_font.render("ŠACHOVÁ HRA", True, (255, 255, 255))
        title_rect = title.get_rect(center=(TOTAL_WIDTH // 2, 80))
        
        title_shadow = self.title_font.render("ŠACHOVÁ HRA", True, (0, 0, 0))
        shadow_rect = title_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        button_y = 250
        button_width = 280
        
        button_height = 80
        button_spacing = 40
        
        total_buttons_width = button_width * 2 + button_spacing
        start_x = (TOTAL_WIDTH - total_buttons_width) // 2
        
        button1_rect = pygame.Rect(start_x, button_y, button_width, button_height)
        
        if button1_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (40, 40, 40), button1_rect, border_radius=10)
        else:
            pygame.draw.rect(self.screen, (20, 20, 20), button1_rect, border_radius=10)
        
        pygame.draw.rect(self.screen, (255, 255, 255), button1_rect, 3, border_radius=10)
        
        play_text = self.message_font.render("NORMÁLNA HRA", True, (255, 255, 255))
        play_rect = play_text.get_rect(center=button1_rect.center)
        self.screen.blit(play_text, play_rect)
        
        desc1 = self.small_font.render("Klasický šach s AI", True, (200, 200, 200))
        desc1_rect = desc1.get_rect(center=(button1_rect.centerx, button1_rect.bottom + 25))
        self.screen.blit(desc1, desc1_rect)
        
        button2_rect = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height)
        
        if button2_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (60, 80, 120), button2_rect, border_radius=10)
        else:
            pygame.draw.rect(self.screen, (40, 60, 100), button2_rect, border_radius=10)
        
        pygame.draw.rect(self.screen, BLUE, button2_rect, 3, border_radius=10)
        
        train_text = self.message_font.render("TRÉNING S AI", True, BLUE)
        train_rect = train_text.get_rect(center=button2_rect.center)
        self.screen.blit(train_text, train_rect)
        
        desc2 = self.small_font.render("AI sa učí z tvojich ťahov", True, (150, 180, 255))
        desc2_rect = desc2.get_rect(center=(button2_rect.centerx, button2_rect.bottom + 25))
        self.screen.blit(desc2, desc2_rect)
        
        return button1_rect, button2_rect
    
    def start_normal_game(self):
        self.training_mode = False
        self.game_started = True
        self.ai_enabled = False
        self.captured_white = []
        self.captured_black = []
        print("\n" + "="*50)
        print(" NORMÁLNA HRA - Klasický šach")
        print("="*50)
    
    def start_training_game(self):
        self.training_mode = True
        self.game_started = True
        self.ai_enabled = True
        self.captured_white = []
        self.captured_black = []
        
        self.player_profile = PlayerProfile()
        self.adaptive_ai = OptimizedAdaptiveAI(PieceColor.BLACK, self.player_profile)
        self.move_number = 0
        self.player_profile.games_played += 1
    
    def draw_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_GRAY if (row + col) % 2 == 0 else DARK_GRAY
                pygame.draw.rect(self.screen, color, 
                               (col * SQUARE_SIZE, row * SQUARE_SIZE, 
                                SQUARE_SIZE, SQUARE_SIZE))
    
    def draw_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece:
                    piece.draw(self.screen, col * SQUARE_SIZE, row * SQUARE_SIZE)
    
    def draw_selected(self):
        if self.selected_pos:
            row, col = self.selected_pos
            x = col * SQUARE_SIZE
            y = row * SQUARE_SIZE
            pygame.draw.rect(self.screen, RED_OUTLINE, (x, y, SQUARE_SIZE, SQUARE_SIZE), 4)
    
    def draw_valid_moves(self):
        for move_row, move_col in self.valid_moves:
            center_x = move_col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = move_row * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(self.screen, RED_OUTLINE, (center_x, center_y), 8)
    
    def draw_captured_pieces(self):
        panel_rect = pygame.Rect(WINDOW_SIZE, 0, CAPTURED_PANEL_WIDTH, WINDOW_SIZE)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        
        pygame.draw.line(self.screen, (100, 100, 100), 
                        (WINDOW_SIZE, 0), (WINDOW_SIZE, WINDOW_SIZE), 2)
        
        x_offset = WINDOW_SIZE + 10
        piece_size = 40
        pieces_per_row = 4
        
        white_title = self.small_font.render("Čierni zozbierali:", True, TEXT_COLOR)
        self.screen.blit(white_title, (x_offset, 10))
        
        y_offset = 50
        
        for i, piece in enumerate(self.captured_white):
            row_num = i // pieces_per_row
            col_num = i % pieces_per_row
            x = x_offset + col_num * (piece_size + 5)
            y = y_offset + row_num * (piece_size + 5)
            
            scaled_image = pygame.transform.scale(piece.image, (piece_size, piece_size))
            self.screen.blit(scaled_image, (x, y))
        
        black_title = self.small_font.render("Bieli zozbierali:", True, TEXT_COLOR)
        self.screen.blit(black_title, (x_offset, WINDOW_SIZE // 2 + 10))
        
        y_offset = WINDOW_SIZE // 2 + 50
        
        for i, piece in enumerate(self.captured_black):
            row_num = i // pieces_per_row
            col_num = i % pieces_per_row
            x = x_offset + col_num * (piece_size + 5)
            y = y_offset + row_num * (piece_size + 5)
            
            scaled_image = pygame.transform.scale(piece.image, (piece_size, piece_size))
            self.screen.blit(scaled_image, (x, y))
    
    def draw_button(self):
        mouse_pos = pygame.mouse.get_pos()
        
        bottom_rect = pygame.Rect(0, WINDOW_SIZE, TOTAL_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, BUTTON_COLOR, bottom_rect)
        
        menu_button_rect = pygame.Rect(0, WINDOW_SIZE, WINDOW_SIZE // 3, BUTTON_HEIGHT)
        
        if menu_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, BUTTON_HOVER, menu_button_rect)
        else:
            pygame.draw.rect(self.screen, BUTTON_COLOR, menu_button_rect)
        
        menu_text = self.font.render("MENU", True, TEXT_COLOR)
        menu_text_rect = menu_text.get_rect(center=menu_button_rect.center)
        self.screen.blit(menu_text, menu_text_rect)
        
        button_rect = pygame.Rect(WINDOW_SIZE // 3, WINDOW_SIZE, WINDOW_SIZE // 3, BUTTON_HEIGHT)
        
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, BUTTON_HOVER, button_rect)
        else:
            pygame.draw.rect(self.screen, BUTTON_COLOR, button_rect)
        
        if self.training_mode:
            if self.ai_thinking:
                status = "AI PREMÝŠĽA..."
                color = (255, 165, 0)
            else:
                level = self.player_profile.analyze_skill_level() if self.player_profile else 1
                status = f"TRÉNING (Lvl {level})"
                color = BLUE
        else:
            if self.ai_thinking:
                status = "AI PREMÝŠĽA..."
                color = (255, 165, 0)
            else:
                status = "AI: ZAPNUTÉ" if self.ai_enabled else "AI: VYPNUTÉ"
                color = GREEN if self.ai_enabled else RED
        
        text = self.small_font.render(status, True, color)
        text_rect = text.get_rect(center=button_rect.center)
        self.screen.blit(text, text_rect)
        
        settings_rect = pygame.Rect(2 * WINDOW_SIZE // 3, WINDOW_SIZE, WINDOW_SIZE // 3, BUTTON_HEIGHT)
        
        if settings_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, BUTTON_HOVER, settings_rect)
        else:
            pygame.draw.rect(self.screen, BUTTON_COLOR, settings_rect)
        
        if self.training_mode and self.player_profile:
            settings_text = self.small_font.render(f"Ťahy: {self.move_number}", True, TEXT_COLOR)
        else:
            from ai_player import AI_DEPTH
            settings_text = self.small_font.render(f"ÚROVEŇ: {AI_DEPTH}", True, TEXT_COLOR)
        
        settings_text_rect = settings_text.get_rect(center=settings_rect.center)
        self.screen.blit(settings_text, settings_text_rect)
        
        pygame.draw.line(self.screen, TEXT_COLOR, 
                        (WINDOW_SIZE // 3, WINDOW_SIZE), 
                        (WINDOW_SIZE // 3, WINDOW_SIZE + BUTTON_HEIGHT), 2)
        pygame.draw.line(self.screen, TEXT_COLOR, 
                        (2 * WINDOW_SIZE // 3, WINDOW_SIZE), 
                        (2 * WINDOW_SIZE // 3, WINDOW_SIZE + BUTTON_HEIGHT), 2)
        
        return menu_button_rect, button_rect, settings_rect
    
    def draw_check_message(self):
        if self.game_over and self.winner:
            message = f"MAT! {'Bieli' if self.winner == PieceColor.WHITE else 'Čierni'} vyhrali!"
            text = self.message_font.render(message, True, RED)
            
            bg_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
            bg_rect.inflate_ip(20, 20)
            s = pygame.Surface(bg_rect.size)
            s.set_alpha(200)
            s.fill((0, 0, 0))
            self.screen.blit(s, bg_rect.topleft)
            
            text_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
            self.screen.blit(text, text_rect)
            
            restart_text = self.font.render("Stlač ENTER pre návrat do menu", True, TEXT_COLOR)
            restart_rect = restart_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 50))
            self.screen.blit(restart_text, restart_rect)
    
    def draw_promotion_menu(self):
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        title = self.message_font.render("Vyber figúrku", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_SIZE // 2, 100))
        self.screen.blit(title, title_rect)
        
        piece_types = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]
        piece_size = 120
        spacing = 20
        total_width = 4 * piece_size + 3 * spacing
        start_x = (WINDOW_SIZE - total_width) // 2
        y = 250
        
        mouse_pos = pygame.mouse.get_pos()
        promotion_buttons = []
        
        for i, piece_type in enumerate(piece_types):
            x = start_x + i * (piece_size + spacing)
            rect = pygame.Rect(x, y, piece_size, piece_size)
            promotion_buttons.append((rect, piece_type))
            
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (100, 100, 150), rect, border_radius=10)
            else:
                pygame.draw.rect(self.screen, (50, 50, 70), rect, border_radius=10)
            
            pygame.draw.rect(self.screen, (200, 200, 200), rect, 3, border_radius=10)
            
            temp_piece = Piece(piece_type, self.promotion_color)
            piece_x = x + (piece_size - temp_piece.image.get_width()) // 2
            piece_y = y + (piece_size - temp_piece.image.get_height()) // 2
            self.screen.blit(temp_piece.image, (piece_x, piece_y))
            
            names = {
                PieceType.QUEEN: "Dáma",
                PieceType.ROOK: "Veža",
                PieceType.BISHOP: "Strelec",
                PieceType.KNIGHT: "Kôň"
            }
            name_text = self.small_font.render(names[piece_type], True, TEXT_COLOR)
            name_rect = name_text.get_rect(center=(x + piece_size // 2, y + piece_size + 30))
            self.screen.blit(name_text, name_rect)
        
        return promotion_buttons
    
    def handle_click(self, pos):
        if self.game_over:
            return
        
        if self.promotion_active:
            promotion_buttons = self.draw_promotion_menu()
            for rect, piece_type in promotion_buttons:
                if rect.collidepoint(pos):
                    new_piece = Piece(piece_type, self.promotion_color)
                    self.board.set_piece(*self.promotion_pos, new_piece)
                    new_piece.has_moved = True
                    
                    self.promotion_active = False
                    self.promotion_pos = None
                    self.promotion_color = None
                    
                    self.check_game_state()
                    return
            return
        
        if pos[1] >= WINDOW_SIZE:
            menu_btn, ai_btn, settings_btn = self.get_button_rects()
            
            if menu_btn.collidepoint(pos):
                self.return_to_menu()
                return
            elif ai_btn.collidepoint(pos):
                if not self.ai_thinking and not self.training_mode:
                    self.ai_enabled = not self.ai_enabled
            elif settings_btn.collidepoint(pos):
                if not self.training_mode:
                    self.cycle_ai_difficulty()
            return
        
        if self.ai_enabled and self.game_logic.current_turn == PieceColor.BLACK:
            return
        
        col = pos[0] // SQUARE_SIZE
        row = pos[1] // SQUARE_SIZE
        
        if col >= 8:
            return
        
        if self.selected_piece:
            if (row, col) in self.valid_moves:
                target = self.board.get_piece(row, col)
                if target:
                    if target.color == PieceColor.WHITE:
                        self.captured_white.append(target)
                    else:
                        self.captured_black.append(target)
                
                if self.training_mode and self.player_profile:
                    piece = self.board.get_piece(*self.selected_pos)
                    was_capture = target is not None
                    self.move_number += 1
                    
                    self.player_profile.record_move(
                        self.selected_pos, (row, col),
                        piece.type, was_capture, self.move_number
                    )
                
                moved_piece = self.board.get_piece(*self.selected_pos)
                self.game_logic.move_piece(self.selected_pos, (row, col))
                
                if moved_piece.type == PieceType.PAWN:
                    if (moved_piece.color == PieceColor.WHITE and row == 0) or \
                       (moved_piece.color == PieceColor.BLACK and row == 7):
                        self.promotion_active = True
                        self.promotion_pos = (row, col)
                        self.promotion_color = moved_piece.color
                        self.selected_piece = None
                        self.selected_pos = None
                        self.valid_moves = []
                        return
                
                self.check_game_state()
                self.selected_piece = None
                self.selected_pos = None
                self.valid_moves = []
            else:
                self.try_select_piece(row, col)
        else:
            self.try_select_piece(row, col)
    
    def get_button_rects(self):
        menu_btn = pygame.Rect(0, WINDOW_SIZE, WINDOW_SIZE // 3, BUTTON_HEIGHT)
        ai_btn = pygame.Rect(WINDOW_SIZE // 3, WINDOW_SIZE, WINDOW_SIZE // 3, BUTTON_HEIGHT)
        settings_btn = pygame.Rect(2 * WINDOW_SIZE // 3, WINDOW_SIZE, WINDOW_SIZE // 3, BUTTON_HEIGHT)
        return menu_btn, ai_btn, settings_btn
    
    def return_to_menu(self):
        if self.training_mode and self.player_profile:
            self.player_profile.save_profile()
        
        self.board = Board()
        self.game_logic = GameLogic(self.board)
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []
        self.ai_thinking = False
        self.game_over = False
        self.winner = None
        self.check_status = None
        self.counter = 0
        self.game_started = False
        self.training_mode = False
        self.move_number = 0
        self.ai_enabled = False
        self.captured_white = []
        self.captured_black = []
        self.promotion_active = False
        self.promotion_pos = None
        self.promotion_color = None
        print("\n Návrat do menu")
    
    def cycle_ai_difficulty(self):
        import ai_player
        ai_player.AI_DEPTH = (ai_player.AI_DEPTH % 4) + 1
        self.ai_player = AIPlayer(PieceColor.BLACK)
    
    def try_select_piece(self, row, col):
        piece = self.board.get_piece(row, col)
        if piece and piece.color == self.game_logic.current_turn:
            self.selected_piece = piece
            self.selected_pos = (row, col)
            self.valid_moves = self.get_valid_moves_with_check_filter(row, col)
        else:
            self.selected_piece = None
            self.selected_pos = None
            self.valid_moves = []
    
    def get_valid_moves_with_check_filter(self, row, col):
        piece = self.board.get_piece(row, col)
        if not piece:
            return []
        all_moves = self.game_logic.get_valid_moves(row, col)
        valid_moves = []
        for to_row, to_col in all_moves:
            game_logic_copy = copy.deepcopy(self.game_logic)
            game_logic_copy.move_piece((row, col), (to_row, to_col))
            board_copy = game_logic_copy.board
            king_pos = None
            for kr in range(8):
                for kc in range(8):
                    p = board_copy.get_piece(kr, kc)
                    if p and p.type == PieceType.KING and p.color == piece.color:
                        king_pos = (kr, kc)
                        break
                if king_pos:
                    break
            in_check = False
            if king_pos:
                opponent_color = PieceColor.BLACK if piece.color == PieceColor.WHITE else PieceColor.WHITE
                for r in range(8):
                    for c in range(8):
                        op = board_copy.get_piece(r, c)
                        if op and op.color == opponent_color:
                            moves = game_logic_copy.get_valid_moves(r, c)
                            if king_pos in moves:
                                in_check = True
                                break
                    if in_check:
                        break
            if not in_check:
                valid_moves.append((to_row, to_col))
        return valid_moves
    
    def make_ai_move(self):
        if self.training_mode and self.adaptive_ai:
            ai_move = self.adaptive_ai.get_move(self.board, self.game_logic)
        else:
            ai_move = self.ai_player.get_move(self.board, self.game_logic)
        
        if ai_move:
            from_pos, to_pos = ai_move
            
            target = self.board.get_piece(*to_pos)
            if target:
                if target.color == PieceColor.WHITE:
                    self.captured_white.append(target)
                else:
                    self.captured_black.append(target)
            
            moved_piece = self.board.get_piece(*from_pos)
            self.game_logic.move_piece(from_pos, to_pos)
            
            if moved_piece.type == PieceType.PAWN:
                to_row, to_col = to_pos
                if (moved_piece.color == PieceColor.WHITE and to_row == 0) or \
                   (moved_piece.color == PieceColor.BLACK and to_row == 7):
                    new_piece = Piece(PieceType.QUEEN, moved_piece.color)
                    self.board.set_piece(to_row, to_col, new_piece)
                    new_piece.has_moved = True
            
            self.check_game_state()
            self.selected_piece = None
            self.selected_pos = None
            self.valid_moves = []
        
        self.ai_thinking = False
    
    def check_game_state(self):
        current_color = self.game_logic.current_turn
        
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.type == PieceType.KING and piece.color == current_color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if not king_pos:
            self.game_over = True
            self.winner = PieceColor.BLACK if current_color == PieceColor.WHITE else PieceColor.WHITE
            
            if self.training_mode and self.player_profile:
                if self.winner == PieceColor.WHITE:
                    self.player_profile.wins += 1
                else:
                    self.player_profile.losses += 1
                self.player_profile.save_profile()
            return
        
        in_check = self.is_square_attacked(king_pos, current_color)
        
        if in_check:
            has_valid_moves = False
            
            for row in range(8):
                for col in range(8):
                    piece = self.board.get_piece(row, col)
                    if piece and piece.color == current_color:
                        valid_moves = self.get_valid_moves_with_check_filter(row, col)
                        if valid_moves:
                            has_valid_moves = True
                            break
                if has_valid_moves:
                    break
            
            if not has_valid_moves:
                self.game_over = True
                self.winner = PieceColor.BLACK if current_color == PieceColor.WHITE else PieceColor.WHITE
                
                if self.training_mode and self.player_profile:
                    if self.winner == PieceColor.WHITE:
                        self.player_profile.wins += 1
                    else:
                        self.player_profile.losses += 1
                    self.player_profile.save_profile()
    
    def is_square_attacked(self, square, color):
        opponent_color = PieceColor.BLACK if color == PieceColor.WHITE else PieceColor.WHITE
        
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == opponent_color:
                    original_turn = self.game_logic.current_turn
                    self.game_logic.current_turn = opponent_color
                    moves = self.game_logic.get_valid_moves(row, col)
                    self.game_logic.current_turn = original_turn
                    
                    if square in moves:
                        return True
        
        return False
    
    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            if self.counter < 30:
                self.counter += 1
            else:
                self.counter = 0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.training_mode and self.player_profile:
                        self.player_profile.save_profile()
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_started:
                        button1, button2 = self.draw_menu()
                        if button1.collidepoint(pygame.mouse.get_pos()):
                            self.start_normal_game()
                        elif button2.collidepoint(pygame.mouse.get_pos()):
                            self.start_training_game()
                    else:
                        self.handle_click(pygame.mouse.get_pos())
                elif event.type == pygame.KEYDOWN:
                    if self.game_started:
                        if event.key == pygame.K_a and not self.training_mode:
                            if not self.ai_thinking:
                                self.ai_enabled = not self.ai_enabled
                        if event.key == pygame.K_RETURN and self.game_over:
                            self.return_to_menu()
                        if event.key == pygame.K_m:
                            self.return_to_menu()
                        if event.key == pygame.K_1 and not self.training_mode:
                            self.set_ai_difficulty(1)
                        elif event.key == pygame.K_2 and not self.training_mode:
                            self.set_ai_difficulty(2)
                        elif event.key == pygame.K_3 and not self.training_mode:
                            self.set_ai_difficulty(3)
                        elif event.key == pygame.K_4 and not self.training_mode:
                            self.set_ai_difficulty(4)
            
            if not self.game_started:
                self.draw_menu()
            else:
                if self.ai_enabled and self.game_logic.current_turn == PieceColor.BLACK and not self.ai_thinking and not self.game_over:
                    self.ai_thinking = True
                    self.ai_move_time = current_time + AI_DELAY
                
                if self.ai_thinking and current_time >= self.ai_move_time:
                    self.make_ai_move()
                
                self.draw_board()
                self.draw_pieces()
                self.draw_valid_moves()
                self.draw_selected()
                self.draw_captured_pieces()
                self.draw_check_message()
                self.draw_button()
                
                if self.promotion_active:
                    self.draw_promotion_menu()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def set_ai_difficulty(self, level):
        import ai_player
        ai_player.AI_DEPTH = level
        self.ai_player = AIPlayer(PieceColor.BLACK)

if __name__ == "__main__":
    game = ChessGame()
    
    print("\nVÝBER REŽIMU:\n")
    print("  1. NORMÁLNA HRA - Klasický šach s AI rôznych úrovní")
    print("  2. TRÉNING S AI - AI sa učí z tvojich ťahov!")
    print("\nV HRE:\n")
    print("  - Klikni na figúrku a potom na červenú bodku")
    print("  - Stlač 'A' (len normálny režim): AI ON/OFF")
    print("  - Stlač 'M' alebo klikni MENU: Návrat do menu")
    print("  - Stlač '1-4' (len normálny režim): Nastav úroveň")
    print("  - Stlač ENTER: Návrat do menu po skončení hry")
    print("  - Pravý panel: Zozbierané figúrky")
    print("\nTRÉNINGOVÝ REŽIM:\n")
    print("  - AI sleduje tvoje ťahy a ukladá ich do 'player_profile.json'")
    print("  - AI sa priebežne prispôsobí tvojej úrovni a štýlu\n")
    
    game.run()