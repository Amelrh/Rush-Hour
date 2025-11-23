#interface.py 
import pygame
import sys
import time
import math
import random
from typing import Optional, List, Tuple

# ============================================================================
# CONFIGURATION ET CONSTANTES - Optimisé pour mode horizontal avec rose clair
# ============================================================================

CELL_SIZE = 70  
MARGIN = 50
TITLE_HEIGHT = 100
FPS = 60

BG_COLOR = (35, 20, 28)
BG_GRADIENT_TOP = (50, 25, 45)
BG_GRADIENT_BOTTOM = (25, 15, 22)
GRID_COLOR = (100, 60, 85)
GRID_GLOW = (200, 120, 180, 80)
HUD_COLOR = (50, 30, 45)
TEXT_COLOR = (255, 240, 250)
ACCENT_COLOR = (255, 150, 200)  # Rose clair
SUCCESS_COLOR = (255, 180, 220)  # Rose succès
WALL_COLOR = (120, 80, 100)
BUTTON_COLOR = (200, 50, 50)
BUTTON_HOVER_COLOR = (255, 80, 80)

CAR_COLORS = [
    (255, 80, 80),    # X - Rouge 
    (80, 220, 120),   # A - Vert émeraude
    (80, 150, 255),   # B - Bleu ciel
    (255, 200, 80),   # C - Jaune doré
    (160, 80, 220),   # D - Violet
    (80, 230, 230),   # E - Cyan
    (255, 140, 80),   # F - Orange
    (120, 200, 80),   # G - Vert lime
    (100, 180, 255),  # H - Bleu clair
    (255, 180, 120),  # I - Pêche
    (180, 120, 255),  # J - Lavande
    (80, 200, 180),   # K - Turquoise
    (220, 180, 80),   # L - Or
    (140, 100, 200),  # M - Pourpre
    (100, 220, 200),  # N - Menthe
    (200, 100, 180),   # O - Rose
]

MAX_PARTICLES = 150
MAX_PARTICLES_PER_VEHICLE = 20

# ============================================================================
# CLASSE PARTICLE
# ============================================================================

class Particle:
    """Particule pour effets visuels avec gestion optimisée"""
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = 1.0
        self.size = random.randint(3, 8)
    
    def update(self, dt):
        """Met à jour la position et la durée de vie"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 200 * dt  # Gravité
        self.life -= dt * 2
        return self.life > 0
    
    def draw(self, screen):
        """Dessine la particule avec transparence"""
        alpha = int(self.life * 255)
        color = (*self.color[:3], alpha)
        size = int(self.size * self.life)
        if size > 0:
            surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (size, size), size)
            screen.blit(surf, (int(self.x - size), int(self.y - size)))

# ============================================================================
# CLASSE ANIMATED VEHICLE
# ============================================================================

class AnimatedVehicle:
    """Véhicule avec animation de position et rotation"""
    def __init__(self, vehicle, idx):
        self.vehicle = vehicle
        self.idx = idx
        self.target_x = vehicle.x
        self.target_y = vehicle.y
        self.current_x = float(vehicle.x)
        self.current_y = float(vehicle.y)
        self.animation_speed = 8.0
        self.scale = 0.0  
        self.rotation = 0.0
        self.wheel_rotation = 0.0
        self.particle_count = 0
        
    def update(self, dt):
        """Met à jour la position et l'animation"""
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        
        if abs(dx) > 0.01:
            self.current_x += dx * self.animation_speed * dt
        else:
            self.current_x = self.target_x
            
        if abs(dy) > 0.01:
            self.current_y += dy * self.animation_speed * dt
        else:
            self.current_y = self.target_y
        
        if self.scale < 1.0:
            self.scale = min(1.0, self.scale + dt * 3)
            self.rotation = (1.0 - self.scale) * 360
        
        if self.is_moving():
            self.wheel_rotation += dt * 360 * 2
            self.wheel_rotation %= 360
    
    def sync_position(self):
        """Synchronise avec la position du véhicule"""
        self.target_x = self.vehicle.x
        self.target_y = self.vehicle.y
    
    def is_moving(self):
        """Vérifie si le véhicule est en mouvement"""
        return abs(self.current_x - self.target_x) > 0.01 or abs(self.current_y - self.target_y) > 0.01

# ============================================================================
# CLASSE BUTTON - Bouton amélioré avec meilleur positionnement
# ============================================================================

class Button:
    """Bouton interactif avec meilleur feedback"""
    def __init__(self, x, y, width, height, text, font_size=18):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.is_hovered = False
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER_COLOR
        self.click_time = 0
    
    def update(self, mouse_pos):
        """Met à jour l'état du bouton"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen):
        """Dessine le bouton avec effet de survol"""
        color = self.hover_color if self.is_hovered else self.color
        
        # Ombre du bouton
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # Bouton principal
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=8)
        
        # Texte du bouton
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, event):
        """Vérifie si le bouton est cliqué"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.rect.collidepoint(event.pos)
        return False

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_car_color(idx):
    """Retourne la couleur du véhicule selon son index"""
    return CAR_COLORS[idx % len(CAR_COLORS)]

def draw_gradient_background(screen):
    """Dessine un fond avec dégradé lisse"""
    width, height = screen.get_size()
    for y in range(height):
        ratio = y / height
        color = tuple(int(BG_GRADIENT_TOP[i] * (1 - ratio) + BG_GRADIENT_BOTTOM[i] * ratio) for i in range(3))
        pygame.draw.line(screen, color, (0, y), (width, y))

def draw_glowing_grid(screen, puzzle, time_offset):
    """Grille avec effet de lueur animée et murs"""
    for y_row in range(puzzle.board_height):
        for x_col in range(puzzle.board_width):
            rect = pygame.Rect(
                MARGIN + x_col * CELL_SIZE,
                TITLE_HEIGHT + MARGIN + y_row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            
            pulse = math.sin(time_offset * 2 + (x_col + y_row) * 0.3) * 0.3 + 0.7
            glow_alpha = int(pulse * 40)
            
            glow_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*GRID_GLOW[:3], glow_alpha), glow_surf.get_rect(), border_radius=12)
            screen.blit(glow_surf, rect.topleft)
    
            pygame.draw.rect(screen, GRID_COLOR, rect, 2, border_radius=12)
            
            if (x_col, y_row) in puzzle.walls:
                pygame.draw.rect(screen, WALL_COLOR, rect, border_radius=8)
                pygame.draw.rect(screen, (150, 150, 150), rect, 2, border_radius=8)

# ============================================================================
# FONCTIONS DE DESSIN DES VÉHICULES
# ============================================================================

def draw_wheel(screen, x, y, radius, rotation):
    """Dessine une roue animée avec rotation"""
    wheel_color = (40, 40, 40)
    wheel_rim = (180, 180, 180)
    
    pygame.draw.circle(screen, wheel_color, (x, y), radius)
    pygame.draw.circle(screen, wheel_rim, (x, y), radius - 4)
    
    num_spokes = 6
    for i in range(num_spokes):
        angle = (i * 360 / num_spokes + rotation) * math.pi / 180
        spoke_x = x + (radius - 6) * math.cos(angle)
        spoke_y = y + (radius - 6) * math.sin(angle)
        pygame.draw.line(screen, (100, 100, 100), (x, y), (spoke_x, spoke_y), 2)

def draw_realistic_car(screen, rect, color, orientation, is_target_car, time_offset, vehicle_length, wheel_rotation=0):
    """Dessine une voiture réaliste avec ombres et effets"""
    shadow = rect.copy()
    shadow.x += 6
    shadow.y += 6
    shadow_surf = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(), border_radius=20)
    screen.blit(shadow_surf, shadow.topleft)
    
    is_truck = vehicle_length >= 2
    
    if is_truck:
        draw_truck(screen, rect, color, orientation, time_offset, wheel_rotation)
    else:
        draw_small_car(screen, rect, color, orientation, time_offset, wheel_rotation)
    
    shine_offset = math.sin(time_offset * 2) * 5
    ellipse_rect = pygame.Rect(
        rect.x + rect.width // 4 + shine_offset,
        rect.y + rect.height // 6,
        rect.width // 2,
        rect.height // 4
    )
    shine_surf = pygame.Surface((ellipse_rect.width, ellipse_rect.height), pygame.SRCALPHA)
    pygame.draw.ellipse(shine_surf, (255, 255, 255, 100), shine_surf.get_rect())
    screen.blit(shine_surf, ellipse_rect.topleft)

def draw_small_car(screen, rect, color, orientation, time_offset, wheel_rotation=0):
    """Dessine une petite voiture avec détails"""
    car_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for i in range(rect.height):
        ratio = i / rect.height
        darker = tuple(int(color[j] * (0.7 + ratio * 0.3)) for j in range(3))
        pygame.draw.line(car_surf, darker, (0, i), (rect.width, i))
    pygame.draw.rect(car_surf, color, car_surf.get_rect(), 3, border_radius=20)
    screen.blit(car_surf, rect.topleft)

    window_color = (100, 150, 200, 180)
    window_border = (60, 90, 120)
    
    if orientation == 'H':
        window = pygame.Rect(
            rect.x + rect.width * 0.3,
            rect.y + rect.height * 0.2,
            rect.width * 0.4,
            rect.height * 0.6
        )
        window_surf = pygame.Surface((window.width, window.height), pygame.SRCALPHA)
        pygame.draw.rect(window_surf, window_color, window_surf.get_rect(), border_radius=8)
        pygame.draw.rect(window_surf, window_border, window_surf.get_rect(), 2, border_radius=8)
        screen.blit(window_surf, window.topleft)
        
        headlight_color = (255, 255, 200)
        pygame.draw.circle(screen, headlight_color, (rect.right - 8, rect.y + rect.height // 3), 4)
        pygame.draw.circle(screen, headlight_color, (rect.right - 8, rect.bottom - rect.height // 3), 4)
        
        taillight_color = (255, 50, 50)
        pygame.draw.circle(screen, taillight_color, (rect.x + 8, rect.y + rect.height // 3), 3)
        pygame.draw.circle(screen, taillight_color, (rect.x + 8, rect.bottom - rect.height // 3), 3)
        
        draw_wheel(screen, rect.right - 15, rect.bottom + 2, 10, wheel_rotation)
        draw_wheel(screen, rect.x + 15, rect.bottom + 2, 10, wheel_rotation)
        
    else:
        window = pygame.Rect(
            rect.x + rect.width * 0.2,
            rect.y + rect.height * 0.3,
            rect.width * 0.6,
            rect.height * 0.4
        )
        window_surf = pygame.Surface((window.width, window.height), pygame.SRCALPHA)
        pygame.draw.rect(window_surf, window_color, window_surf.get_rect(), border_radius=8)
        pygame.draw.rect(window_surf, window_border, window_surf.get_rect(), 2, border_radius=8)
        screen.blit(window_surf, window.topleft)
        
        headlight_color = (255, 255, 200)
        pygame.draw.circle(screen, headlight_color, (rect.x + rect.width // 3, rect.bottom - 8), 4)
        pygame.draw.circle(screen, headlight_color, (rect.right - rect.width // 3, rect.bottom - 8), 4)
        
        taillight_color = (255, 50, 50)
        pygame.draw.circle(screen, taillight_color, (rect.x + rect.width // 3, rect.y + 8), 3)
        pygame.draw.circle(screen, taillight_color, (rect.right - rect.width // 3, rect.y + 8), 3)
        
        draw_wheel(screen, rect.right + 2, rect.bottom - 15, 10, wheel_rotation)
        draw_wheel(screen, rect.right + 2, rect.y + 15, 10, wheel_rotation)

def draw_truck(screen, rect, color, orientation, time_offset, wheel_rotation=0):
    """Dessine un camion avec détails"""
    truck_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    for i in range(rect.height):
        ratio = i / rect.height
        darker = tuple(int(color[j] * (0.6 + ratio * 0.4)) for j in range(3))
        pygame.draw.line(truck_surf, darker, (0, i), (rect.width, i))
    
    pygame.draw.rect(truck_surf, color, truck_surf.get_rect(), 4, border_radius=15)
    screen.blit(truck_surf, rect.topleft)
    
    window_color = (100, 150, 200, 180)
    window_border = (60, 90, 120)
    
    if orientation == 'H':
        cabin_window = pygame.Rect(
            rect.x + rect.width * 0.75,
            rect.y + rect.height * 0.15,
            rect.width * 0.18,
            rect.height * 0.7
        )
        window_surf = pygame.Surface((cabin_window.width, cabin_window.height), pygame.SRCALPHA)
        pygame.draw.rect(window_surf, window_color, window_surf.get_rect(), border_radius=6)
        pygame.draw.rect(window_surf, window_border, window_surf.get_rect(), 2, border_radius=6)
        screen.blit(window_surf, cabin_window.topleft)
        
        separator_x = rect.x + rect.width * 0.7
        pygame.draw.line(screen, (0, 0, 0, 100), (separator_x, rect.y + 5), (separator_x, rect.bottom - 5), 3)
        
        headlight_color = (255, 255, 200)
        pygame.draw.circle(screen, headlight_color, (rect.right - 6, rect.y + rect.height // 3), 6)
        pygame.draw.circle(screen, headlight_color, (rect.right - 6, rect.bottom - rect.height // 3), 6)
        
        taillight_color = (255, 50, 50)
        pygame.draw.circle(screen, taillight_color, (rect.x + 8, rect.y + rect.height // 3), 5)
        pygame.draw.circle(screen, taillight_color, (rect.x + 8, rect.bottom - rect.height // 3), 5)
        
        draw_wheel(screen, rect.right - 18, rect.bottom + 2, 12, wheel_rotation)
        draw_wheel(screen, rect.x + 25, rect.bottom + 2, 12, wheel_rotation)
        draw_wheel(screen, rect.x + 45, rect.bottom + 2, 12, wheel_rotation)
        
    else:
        cabin_window = pygame.Rect(
            rect.x + rect.width * 0.15,
            rect.y + rect.height * 0.75,
            rect.width * 0.7,
            rect.height * 0.18
        )
        window_surf = pygame.Surface((cabin_window.width, cabin_window.height), pygame.SRCALPHA)
        pygame.draw.rect(window_surf, window_color, window_surf.get_rect(), border_radius=6)
        pygame.draw.rect(window_surf, window_border, window_surf.get_rect(), 2, border_radius=6)
        screen.blit(window_surf, cabin_window.topleft)
        
        separator_y = rect.y + rect.height * 0.7
        pygame.draw.line(screen, (0, 0, 0, 100), (rect.x + 5, separator_y), (rect.right - 5, separator_y), 3)
        
        headlight_color = (255, 255, 200)
        pygame.draw.circle(screen, headlight_color, (rect.x + rect.width // 3, rect.bottom - 6), 6)
        pygame.draw.circle(screen, headlight_color, (rect.right - rect.width // 3, rect.bottom - 6), 6)
        
        taillight_color = (255, 50, 50)
        pygame.draw.circle(screen, taillight_color, (rect.x + rect.width // 3, rect.y + 8), 5)
        pygame.draw.circle(screen, taillight_color, (rect.right - rect.width // 3, rect.y + 8), 5)
        
        draw_wheel(screen, rect.right + 2, rect.bottom - 18, 12, wheel_rotation)
        draw_wheel(screen, rect.right + 2, rect.y + 25, 12, wheel_rotation)
        draw_wheel(screen, rect.right + 2, rect.y + 45, 12, wheel_rotation)

def draw_animated_vehicle(screen, anim_vehicle, time_offset, particles):
    """Dessine un véhicule avec animations"""
    v = anim_vehicle.vehicle
    idx = anim_vehicle.idx
    color = get_car_color(idx)

    x_pos = MARGIN + anim_vehicle.current_x * CELL_SIZE
    y_pos = TITLE_HEIGHT + MARGIN + anim_vehicle.current_y * CELL_SIZE
    
    if v.orientation == 'H':
        width = CELL_SIZE * v.length
        height = CELL_SIZE
    else:
        width = CELL_SIZE
        height = CELL_SIZE * v.length
    
    scale_factor = anim_vehicle.scale
    if idx == 0:  
        pulse = math.sin(time_offset * 3) * 0.05 + 1.0
        scale_factor *= pulse
    
    scaled_width = int(width * scale_factor)
    scaled_height = int(height * scale_factor)
    offset_x = (width - scaled_width) // 2
    offset_y = (height - scaled_height) // 2
    
    rect = pygame.Rect(
        int(x_pos + offset_x),
        int(y_pos + offset_y),
        scaled_width,
        scaled_height
    )
    
    draw_realistic_car(screen, rect, color, v.orientation, idx == 0, time_offset, v.length, anim_vehicle.wheel_rotation)
    
    font = pygame.font.SysFont("Arial", 36, bold=True)
    text_shadow = font.render(v.id, True, (0, 0, 0))
    screen.blit(text_shadow, (rect.centerx - 10, rect.centery - 16))
    
    text = font.render(v.id, True, (255, 255, 255))
    screen.blit(text, (rect.centerx - 12, rect.centery - 18))
    
    if anim_vehicle.is_moving() and random.random() < 0.3 and anim_vehicle.particle_count < MAX_PARTICLES_PER_VEHICLE and len(particles) < MAX_PARTICLES:
        particle_color = color
        velocity = (random.uniform(-50, 50), random.uniform(-50, 0))
        particles.append(Particle(rect.centerx, rect.centery, particle_color, velocity))
        anim_vehicle.particle_count += 1

def create_success_particles(screen_width, screen_height):
    """Crée des particules de célébration"""
    particles = []
    for _ in range(100):
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        color = random.choice(CAR_COLORS)
        velocity = (random.uniform(-100, 100), random.uniform(-300, -100))
        particles.append(Particle(x, y, color, velocity))
    return particles

# ============================================================================
# FONCTIONS D'AFFICHAGE HUD ET MESSAGES
# ============================================================================

def draw_success_message(screen, time_offset, moves_count, elapsed_time, algorithm_name=""):
    """Affiche le message de victoire avec animations"""
    width, height = screen.get_width(), screen.get_height()
    
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
    screen.blit(overlay, (0, 0))
    
    scale = abs(math.sin(time_offset * 2)) * 0.2 + 1.0
    
    font_big = pygame.font.SysFont("Bahnschrift", int(72 * scale), bold=True)
    text = "🎉 VICTOIRE ! 🎉"

    rainbow_offset = int(time_offset * 100) % 360
    color_r = int(127 + 127 * math.sin(math.radians(rainbow_offset)))
    color_g = int(127 + 127 * math.sin(math.radians(rainbow_offset + 120)))
    color_b = int(127 + 127 * math.sin(math.radians(rainbow_offset + 240)))
    
    text_surface = font_big.render(text, True, (color_r, color_g, color_b))
    text_rect = text_surface.get_rect(center=(width // 2, height // 2 - 60))
    screen.blit(text_surface, text_rect)
    
    font_stats = pygame.font.SysFont("Segoe UI", 32, bold=True)
    stats_text = f"Résolu en {moves_count} coups et {elapsed_time:.1f}s"
    
    stats_shadow = font_stats.render(stats_text, True, (0, 0, 0))
    screen.blit(stats_shadow, (width // 2 - 200, height // 2 + 42))
    
    stats_surface = font_stats.render(stats_text, True, SUCCESS_COLOR)
    stats_rect = stats_surface.get_rect(center=(width // 2, height // 2 + 40))
    screen.blit(stats_surface, stats_rect)
    
    font_algo = pygame.font.SysFont("Segoe UI", 24, bold=True)
    algo_text = f"Algorithme: {algorithm_name}"
    algo_surface = font_algo.render(algo_text, True, ACCENT_COLOR)
    algo_rect = algo_surface.get_rect(center=(width // 2, height // 2 + 90))
    screen.blit(algo_surface, algo_rect)

def draw_failure_message(screen, time_offset):
    """Affiche le message d'échec"""
    width, height = screen.get_width(), screen.get_height()
    
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
    screen.blit(overlay, (0, 0))
    
    font_big = pygame.font.SysFont("Bahnschrift", 72, bold=True)
    text = "❌ AUCUNE SOLUTION ❌"
    
    text_surface = font_big.render(text, True, (255, 100, 100))
    text_rect = text_surface.get_rect(center=(width // 2, height // 2 - 60))
    screen.blit(text_surface, text_rect)
    
    font_info = pygame.font.SysFont("Segoe UI", 28)
    info_text = "Ce puzzle n'a pas de solution"
    info_surface = font_info.render(info_text, True, (200, 100, 100))
    info_rect = info_surface.get_rect(center=(width // 2, height // 2 + 40))
    screen.blit(info_surface, info_rect)

def draw_hud(screen, moves_count, elapsed_time, time_offset, algorithm_name="", is_solving=False):
    """Dessine le HUD avec titre, mouvements, temps et algorithme - Optimisé pour horizontal"""
    width = screen.get_width()
    height = screen.get_height()
    
    font_title = pygame.font.SysFont("Arial", 20, bold=True)
    title_text = "RUSH HOUR PUZZLE"
    
    outline_surf = font_title.render(title_text, True, (0, 0, 0))
    for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
        screen.blit(outline_surf, (MARGIN + dx, 15 + dy))
    
    title_surface = font_title.render(title_text, True, (255, 255, 255))
    screen.blit(title_surface, (MARGIN, 15))
    
    font_algo = pygame.font.SysFont("Arial", 13, bold=True)
    algo_text = f"Algorithme: {algorithm_name}" if algorithm_name else "Résolution..."
    algo_surface = font_algo.render(algo_text, True, ACCENT_COLOR)
    screen.blit(algo_surface, (MARGIN, 48))
    
    font_subtitle = pygame.font.SysFont("Arial", 16, bold=True)
    subtitle_text = "Libérez la voiture rouge !"
    subtitle_surface = font_subtitle.render(subtitle_text, True, (255, 200, 220))
    screen.blit(subtitle_surface, (MARGIN, 68))
    
    hud_width = 280
    hud_height = 75
    hud_x = width - hud_width - MARGIN
    hud_y = 10
    
    hud_shadow = pygame.Surface((hud_width + 4, hud_height + 4), pygame.SRCALPHA)
    pygame.draw.rect(hud_shadow, (0, 0, 0, 100), hud_shadow.get_rect(), border_radius=12)
    screen.blit(hud_shadow, (hud_x - 2, hud_y - 2))
    
    hud_surf = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
    pygame.draw.rect(hud_surf, (80, 40, 60, 240), hud_surf.get_rect(), border_radius=12)
    pygame.draw.rect(hud_surf, (255, 150, 200), hud_surf.get_rect(), 2, border_radius=12)
    screen.blit(hud_surf, (hud_x, hud_y))
    
    font_label = pygame.font.SysFont("Segoe UI", 14, bold=True)
    font_value = pygame.font.SysFont("Bahnschrift", 28, bold=True)
    
    # Mouvements
    moves_label = font_label.render("MOUVEMENTS", True, (150, 160, 170))
    screen.blit(moves_label, (hud_x + 12, hud_y + 8))
    
    moves_value = font_value.render(str(moves_count), True, (255, 150, 200))
    screen.blit(moves_value, (hud_x + 12, hud_y + 28))
    
    # Temps
    time_label = font_label.render("TEMPS", True, (150, 160, 170))
    screen.blit(time_label, (hud_x + 160, hud_y + 8))
    
    time_text = f"{int(elapsed_time)}s"
    time_value = font_value.render(time_text, True, (255, 150, 200))
    screen.blit(time_value, (hud_x + 160, hud_y + 28))

# ============================================================================
# FONCTION PRINCIPALE D'ANIMATION
# ============================================================================

def animate_solution(puzzle, solution, algorithm_name="A* (h3)"):
    """Animation de la solution avec effets visuels optimisés - Mode horizontal"""
    pygame.init()
    
    width = puzzle.board_width * CELL_SIZE + 2 * MARGIN + 100
    height = puzzle.board_height * CELL_SIZE + 2 * MARGIN + TITLE_HEIGHT + 50
    
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('🚗 Rush Hour - Solution Animée')
    clock = pygame.time.Clock()
    
    quit_button = Button(width - 110, height - 45, 100, 40, "Quitter", font_size=16)
    
    # Initialisation des véhicules animés
    animated_vehicles = [AnimatedVehicle(v, idx) for idx, v in enumerate(puzzle.vehicles)]
    particles = []
    
    start_time = time.time()
    move_index = 0
    move_delay = 0.8  
    last_move_time = start_time
    
    success_particles = []
    show_success = False
    success_start_time = 0
    fixed_elapsed_time = 0
    
    show_failure = solution is None
    failure_start_time = time.time() if show_failure else 0
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        current_time = time.time()
        
        if show_success:
            elapsed = fixed_elapsed_time
        else:
            elapsed = current_time - start_time
        
        mouse_pos = pygame.mouse.get_pos()
        quit_button.update(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if quit_button.is_clicked(event):
                running = False
        
        if show_failure:
            draw_gradient_background(screen)
            draw_glowing_grid(screen, puzzle, elapsed)
            
            for anim_v in animated_vehicles:
                draw_animated_vehicle(screen, anim_v, elapsed, particles)
            
            for p in particles:
                p.draw(screen)
            
            draw_hud(screen, 0, elapsed, elapsed, algorithm_name, is_solving=False)
            draw_failure_message(screen, current_time - failure_start_time)
            
            quit_button.draw(screen)
            
            pygame.display.flip()
            
            if current_time - failure_start_time > 5:
                running = False
            continue
        
        if move_index < len(solution) and current_time - last_move_time >= move_delay:
            puzzle.move_vehicle(solution[move_index])
           
            for anim_v in animated_vehicles:
                anim_v.sync_position()
            move_index += 1
            last_move_time = current_time
            
            if move_index >= len(solution) and puzzle.isGoal():
                show_success = True
                success_start_time = current_time
                fixed_elapsed_time = current_time - start_time
                success_particles = create_success_particles(width, height)
        
        for anim_v in animated_vehicles:
            anim_v.update(dt)
        
        particles = [p for p in particles if p.update(dt)]
        if show_success:
            success_particles = [p for p in success_particles if p.update(dt)]
        
        for anim_v in animated_vehicles:
            if not anim_v.is_moving():
                anim_v.particle_count = 0
       
        # Rendu
        draw_gradient_background(screen)
        draw_glowing_grid(screen, puzzle, elapsed)
       
        for anim_v in animated_vehicles:
            draw_animated_vehicle(screen, anim_v, elapsed, particles)
        
        for p in particles:
            p.draw(screen)
        
        if show_success:
            for p in success_particles:
                p.draw(screen)
            draw_success_message(screen, current_time - success_start_time, len(solution), fixed_elapsed_time, algorithm_name)
        
        draw_hud(screen, move_index, elapsed, elapsed, algorithm_name, is_solving=not show_success)
        
        quit_button.draw(screen)
        
        pygame.display.flip()
        
        if show_success and current_time - success_start_time > 5:
            running = False
    
    pygame.quit()

if __name__ == "__main__":
    print("Ce module nécessite votre classe RushHourPuzzle pour fonctionner.")
    print("Appelez: animate_solution(puzzle, solution, 'BFS') ou animate_solution(puzzle, solution, 'A* (h3)')")