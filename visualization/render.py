"""
This module handles all the Pygame drawing and UI rendering,
including the maze grid, robot, path trail, top HUD, buttons,
and the completion overlay.
"""

import pygame
import math
from typing import List, Tuple, Dict, Any, Optional
from environment.map import MazeMap
from simulation.robot import Robot

# Modern Dark Theme Colors
COLOR_BG = (26, 27, 38)        # Dark grey-blue
COLOR_WALL = (44, 46, 64)      # Slate grey
COLOR_WALL_BORDER = (68, 71, 98)
COLOR_PATH = (47, 93, 128, 120) # Semi-transparent blue for the target path
COLOR_TRAIL = (244, 63, 94)    # Rose-pink for the actual robot path
COLOR_START = (16, 185, 129)   # Emerald green
COLOR_END = (239, 68, 68)      # Coral red
COLOR_DIAMOND = (6, 182, 212)   # Vibrant cyan
COLOR_DIAMOND_GLOW = (34, 211, 238)

COLOR_PID = (234, 179, 8)      # Gold/Yellow
COLOR_FUZZY = (168, 85, 247)   # Purple/Magenta

# HUD & Button Colors
COLOR_HUD_BG = (17, 18, 26)
COLOR_BUTTON = (30, 41, 59)
COLOR_BUTTON_ACTIVE = (59, 130, 246)
COLOR_TEXT = (243, 244, 246)
COLOR_TEXT_MUTED = (156, 163, 175)

class Renderer:
    """Handles rendering of the environment, robot state, and user interface using Pygame."""

    def __init__(self, width: int, height: int):
        """
        Initializes the Renderer.
        
        Args:
            width (int): Window width in pixels.
            height (int): Window height in pixels.
        """
        self.width = width
        self.height = height
        
        # Initialize fonts
        pygame.font.init()
        self.font_large = pygame.font.SysFont("Inter, Arial, Segoe UI", 36, bold=True)
        self.font_medium = pygame.font.SysFont("Inter, Arial, Segoe UI", 20, bold=True)
        self.font_small = pygame.font.SysFont("Inter, Arial, Segoe UI", 14)
        self.font_mono = pygame.font.SysFont("Consolas, Courier New", 12)

        # HUD button rects
        self.btn_pid_rect = pygame.Rect(30, 20, 120, 36)
        self.btn_fuzzy_rect = pygame.Rect(165, 20, 120, 36)
        
        # End screen button rects (to be initialized based on window dimensions)
        self.btn_restart_rect = pygame.Rect(width // 2 - 190, height // 2 + 100, 160, 45)
        self.btn_new_rect = pygame.Rect(width // 2 + 30, height // 2 + 100, 160, 45)

        # Particle systems
        self.particles: List[Dict[str, Any]] = []

    def add_collect_particles(self, x: float, y: float):
        """Adds circular burst particles when a diamond is collected."""
        for _ in range(15):
            angle = math.pi * 2 * (pygame.time.get_ticks() % 100 / 100.0) # Pseudo-random
            speed = 20.0 + (pygame.time.get_ticks() % 50)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,  # 1.0 is full life
                'color': COLOR_DIAMOND,
                'size': 4.0
            })

    def update_particles(self, dt: float):
        """Updates particle physics (friction and fade out)."""
        active_particles = []
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            # Slowly reduce speeds
            p['vx'] *= 0.95
            p['vy'] *= 0.95
            p['life'] -= 2.0 * dt  # Die in half a second
            if p['life'] > 0:
                active_particles.append(p)
        self.particles = active_particles

    def draw_grid(self, surface: pygame.Surface, map_obj: MazeMap):
        """Draws the maze walls, hallways, start, end, and diamonds."""
        cell_size = map_obj.cell_size
        offset_y = map_obj.offset_y
        
        # Draw background/corridors
        surface.fill(COLOR_BG)
        
        # Draw walls
        for col in range(map_obj.cols):
            for row in range(map_obj.rows):
                val = map_obj.grid[col][row]
                x = col * cell_size
                y = row * cell_size + offset_y
                
                if val == 1:
                    # Wall
                    rect = pygame.Rect(x, y, cell_size, cell_size)
                    pygame.draw.rect(surface, COLOR_WALL, rect)
                    pygame.draw.rect(surface, COLOR_WALL_BORDER, rect, 1)
                else:
                    # Corridor grid line
                    rect = pygame.Rect(x, y, cell_size, cell_size)
                    pygame.draw.rect(surface, (33, 35, 48), rect, 1)

        # Draw Start Cell
        s_col, s_row = map_obj.start_grid
        s_x = s_col * cell_size + 4
        s_y = s_row * cell_size + offset_y + 4
        start_rect = pygame.Rect(s_x, s_y, cell_size - 8, cell_size - 8)
        pygame.draw.rect(surface, COLOR_START, start_rect, border_radius=6)
        label_s = self.font_medium.render("S", True, (255, 255, 255))
        surface.blit(label_s, label_s.get_rect(center=start_rect.center))

        # Draw End Cell
        e_col, e_row = map_obj.end_grid
        e_x = e_col * cell_size + 4
        e_y = e_row * cell_size + offset_y + 4
        end_rect = pygame.Rect(e_x, e_y, cell_size - 8, cell_size - 8)
        pygame.draw.rect(surface, COLOR_END, end_rect, border_radius=6)
        label_e = self.font_medium.render("E", True, (255, 255, 255))
        surface.blit(label_e, label_e.get_rect(center=end_rect.center))

        # Draw Diamonds
        # Drawing sparkling cyan diamonds
        for d_col, d_row in map_obj.diamonds:
            cx, cy = map_obj.grid_to_world(d_col, d_row)
            
            # Simple pulsating factor for glow effect
            pulse = math.sin(pygame.time.get_ticks() * 0.006) * 3
            
            # Draw glow
            pygame.draw.circle(surface, (*COLOR_DIAMOND, 80), (int(cx), int(cy)), int(12 + pulse))
            
            # Draw diamond shape polygon
            pts = [
                (cx, cy - 10),  # Top
                (cx + 8, cy),   # Right
                (cx, cy + 10),  # Bottom
                (cx - 8, cy)    # Left
            ]
            pygame.draw.polygon(surface, COLOR_DIAMOND_GLOW, pts)
            pygame.draw.polygon(surface, COLOR_TEXT, pts, 1)

    def draw_path(self, surface: pygame.Surface, robot: Robot):
        """Draws the optimal calculated A* path waypoints and trail."""
        if not robot.waypoints:
            return

        # 1. Draw planned path waypoints
        if len(robot.waypoints) > 1:
            # Create a temporary transparent surface for drawing lines to keep alpha blending working in Pygame
            path_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw lines between waypoints
            pygame.draw.lines(path_surf, (*COLOR_PATH[:3], 100), False, robot.waypoints, 3)
            
            # Draw dots at waypoints
            for idx, pt in enumerate(robot.waypoints):
                is_curr_target = (idx == robot.current_waypoint_idx)
                r = 5 if is_curr_target else 3
                color = COLOR_TEXT if is_curr_target else COLOR_PATH[:3]
                pygame.draw.circle(path_surf, color, (int(pt[0]), int(pt[1])), r)
                
            surface.blit(path_surf, (0, 0))

        # 2. Draw actual robot traveled trail
        if len(robot.telemetry) > 1:
            trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pts = [(log['x'], log['y']) for log in robot.telemetry]
            
            # Group into segments of same controller type to color differently
            current_seg = [pts[0]]
            current_controller = robot.telemetry[0]['controller']
            
            for idx in range(1, len(robot.telemetry)):
                log = robot.telemetry[idx]
                pt = (log['x'], log['y'])
                
                if log['controller'] == current_controller:
                    current_seg.append(pt)
                else:
                    color = COLOR_PID if current_controller == 'PID' else COLOR_FUZZY
                    if len(current_seg) > 1:
                        pygame.draw.lines(trail_surf, (*color, 150), False, current_seg, 2)
                    current_seg = [pts[idx-1], pt] # Joint
                    current_controller = log['controller']
            
            # Draw remaining segment
            if len(current_seg) > 1:
                color = COLOR_PID if current_controller == 'PID' else COLOR_FUZZY
                pygame.draw.lines(trail_surf, (*color, 150), False, current_seg, 2)
                
            surface.blit(trail_surf, (0, 0))

    def draw_robot(self, surface: pygame.Surface, robot: Robot):
        """Draws the robot with its heading arrow and selected controller color scheme."""
        cx, cy = robot.x, robot.y
        theta = robot.theta
        radius = robot.radius
        
        # Determine color based on active controller
        color = COLOR_PID if robot.controller_type == 'PID' else COLOR_FUZZY
        
        # Draw robot base chassis circle with glow
        robot_surf = pygame.Surface((int(radius*3), int(radius*3)), pygame.SRCALPHA)
        rcx, rcy = radius*1.5, radius*1.5
        
        pygame.draw.circle(robot_surf, (*color, 40), (int(rcx), int(rcy)), int(radius * 1.5))
        pygame.draw.circle(robot_surf, color, (int(rcx), int(rcy)), int(radius))
        pygame.draw.circle(robot_surf, COLOR_TEXT, (int(rcx), int(rcy)), int(radius), 2)
        
        # Rotate and blit direction pointer triangle
        # Points of the triangle
        tip_dist = radius
        base_dist = radius * 0.7
        angle_spread = 2.4  # radians
        
        p_tip = (rcx + tip_dist * math.cos(0), rcy + tip_dist * math.sin(0))
        p_left = (rcx + base_dist * math.cos(angle_spread), rcy + base_dist * math.sin(angle_spread))
        p_right = (rcx + base_dist * math.cos(-angle_spread), rcy + base_dist * math.sin(-angle_spread))
        
        pygame.draw.polygon(robot_surf, COLOR_TEXT, [p_tip, p_left, p_right])
        
        # Rotate the whole robot surface or draw directly rotated on original surface
        # Let's draw directly rotated to ensure perfect positioning without Pygame surface rotation artifacts.
        tip = (cx + radius * 1.1 * math.cos(theta), cy + radius * 1.1 * math.sin(theta))
        left = (cx + radius * 0.7 * math.cos(theta + 2.5), cy + radius * 0.7 * math.sin(theta + 2.5))
        right = (cx + radius * 0.7 * math.cos(theta - 2.5), cy + radius * 0.7 * math.sin(theta - 2.5))
        
        # Base glow
        pygame.draw.circle(surface, (*color, 30), (int(cx), int(cy)), int(radius * 1.6))
        pygame.draw.circle(surface, color, (int(cx), int(cy)), int(radius))
        pygame.draw.circle(surface, (17, 18, 26), (int(cx), int(cy)), int(radius - 2)) # hollow center
        
        pygame.draw.polygon(surface, COLOR_TEXT, [tip, left, right])

    def draw_particles(self, surface: pygame.Surface):
        """Draws active particles."""
        for p in self.particles:
            alpha = int(p['life'] * 255)
            # Create a small transparent circle
            p_surf = pygame.Surface((int(p['size'] * 2), int(p['size'] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*p['color'], alpha), (int(p['size']), int(p['size'])), int(p['size']))
            surface.blit(p_surf, (p['x'] - p['size'], p['y'] - p['size']))

    def draw_hud(self, surface: pygame.Surface, robot: Robot, elapsed_time: float, total_diamonds: int, simulation_started: bool = True):
        """Draws the top header bar with controller toggles and status metrics."""
        # Draw HUD Background
        pygame.draw.rect(surface, COLOR_HUD_BG, (0, 0, self.width, 100))
        pygame.draw.line(surface, COLOR_WALL_BORDER, (0, 100), (self.width, 100), 2)
        
        # 1. PID Toggle Button
        pid_active = (robot.controller_type == 'PID') and simulation_started
        pid_btn_color = COLOR_BUTTON_ACTIVE if pid_active else COLOR_BUTTON
        pygame.draw.rect(surface, pid_btn_color, self.btn_pid_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PID if pid_active else COLOR_WALL_BORDER, self.btn_pid_rect, 2, border_radius=6)
        
        label_pid = self.font_medium.render("PID Control", True, COLOR_TEXT)
        surface.blit(label_pid, label_pid.get_rect(center=self.btn_pid_rect.center))
        
        # 2. Fuzzy Toggle Button
        fuzzy_active = (robot.controller_type == 'Fuzzy') and simulation_started
        fuzzy_btn_color = COLOR_BUTTON_ACTIVE if fuzzy_active else COLOR_BUTTON
        pygame.draw.rect(surface, fuzzy_btn_color, self.btn_fuzzy_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_FUZZY if fuzzy_active else COLOR_WALL_BORDER, self.btn_fuzzy_rect, 2, border_radius=6)
        
        label_fuzzy = self.font_medium.render("Fuzzy Control", True, COLOR_TEXT)
        surface.blit(label_fuzzy, label_fuzzy.get_rect(center=self.btn_fuzzy_rect.center))

        # 3. Telemetry Indicators
        # Columns of metrics
        x_start = 320
        y_center = 50
        
        # Time
        time_label = self.font_small.render("TEMPO DE CURSO", True, COLOR_TEXT_MUTED)
        time_val = self.font_medium.render(f"{elapsed_time:.2f} s", True, COLOR_TEXT)
        surface.blit(time_label, (x_start, y_center - 15))
        surface.blit(time_val, (x_start, y_center + 5))
        
        # Speed
        speed_label = self.font_small.render("VELOCIDADE", True, COLOR_TEXT_MUTED)
        speed_val = self.font_medium.render(f"{robot.speed:.1f} px/s", True, COLOR_TEXT)
        surface.blit(speed_label, (x_start + 140, y_center - 15))
        surface.blit(speed_val, (x_start + 140, y_center + 5))
        
        # Diamonds
        collected = len(robot.diamonds_collected)
        diam_label = self.font_small.render("DIAMANTES", True, COLOR_TEXT_MUTED)
        # Glow cyan if all collected, otherwise white
        d_color = COLOR_DIAMOND if collected == total_diamonds else COLOR_TEXT
        diam_val = self.font_medium.render(f"{collected} / {total_diamonds}", True, d_color)
        surface.blit(diam_label, (x_start + 270, y_center - 15))
        surface.blit(diam_val, (x_start + 270, y_center + 5))

        # Controller indicator status box
        status_x = self.width - 220
        status_rect = pygame.Rect(status_x, 25, 190, 50)
        pygame.draw.rect(surface, (23, 23, 33), status_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_WALL_BORDER, status_rect, 1, border_radius=8)
        
        if not simulation_started:
            # Pulsing gray/white color for waiting status
            pulse = int(120 + 80 * math.sin(pygame.time.get_ticks() * 0.005))
            pygame.draw.circle(surface, (pulse, pulse, pulse), (status_x + 20, 50), 6)
            mode_text = self.font_medium.render("AGUARDANDO...", True, (pulse, pulse, pulse))
        else:
            ind_color = COLOR_PID if robot.controller_type == 'PID' else COLOR_FUZZY
            pygame.draw.circle(surface, ind_color, (status_x + 20, 50), 6)
            mode_text = self.font_medium.render(f"MODO: {robot.controller_type}", True, COLOR_TEXT)
            
        surface.blit(mode_text, (status_x + 35, 40))

    def draw_bfs_animation(
        self, 
        surface: pygame.Surface, 
        map_obj: MazeMap, 
        visited_cells: List[Tuple[int, int]], 
        progress: int
    ):
        """Draws the expanding search cells during the initial BFS scanning phase."""
        self.draw_grid(surface, map_obj)
        
        # Create translucent surface for BFS scan overlay
        scan_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        cell_size = map_obj.cell_size
        offset_y = map_obj.offset_y
        
        # Draw cells scanned up to 'progress'
        for i in range(min(progress, len(visited_cells))):
            col, row = visited_cells[i]
            x = col * cell_size
            y = row * cell_size + offset_y
            
            # Fade effect: earlier cells are more transparent, front is brighter cyan
            alpha = int(40 + (i / max(1, progress)) * 140)
            rect = pygame.Rect(x + 2, y + 2, cell_size - 4, cell_size - 4)
            pygame.draw.rect(scan_surf, (6, 182, 212, alpha), rect, border_radius=4)
            
        surface.blit(scan_surf, (0, 0))
        
        # Draw title for the scan phase
        title_rect = pygame.Rect(self.width // 2 - 150, 25, 300, 50)
        pygame.draw.rect(surface, (17, 18, 26, 200), title_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_DIAMOND, title_rect, 1, border_radius=8)
        
        txt = self.font_medium.render("ESCANEANDO MAPA (BFS)", True, COLOR_DIAMOND)
        surface.blit(txt, txt.get_rect(center=title_rect.center))

    def draw_completion_overlay(
        self, 
        surface: pygame.Surface, 
        stats: Dict[str, Any]
    ):
        """Draws a premium overlay menu when the robot reaches the End goal."""
        # 1. Translucent backdrop
        backdrop = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        backdrop.fill((15, 17, 26, 225)) # Very dark overlay
        surface.blit(backdrop, (0, 0))
        
        # 2. Centered statistics panel
        panel_w, panel_h = 500, 360
        panel_x = (self.width - panel_w) // 2
        panel_y = (self.height - panel_h) // 2 - 20
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        pygame.draw.rect(surface, (30, 32, 48), panel_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_WALL_BORDER, panel_rect, 2, border_radius=16)
        
        # Title
        title = self.font_large.render("Circuito Concluído!", True, COLOR_START)
        surface.blit(title, title.get_rect(centerx=self.width // 2, top=panel_y + 25))
        
        # Subtitle query
        subtitle = self.font_small.render("Deseja gerar um novo cenário?", True, COLOR_TEXT_MUTED)
        surface.blit(subtitle, subtitle.get_rect(centerx=self.width // 2, top=panel_y + 70))
        
        # Horizontal divider
        pygame.draw.line(surface, COLOR_WALL_BORDER, (panel_x + 30, panel_y + 95), (panel_x + panel_w - 30, panel_y + 95), 1)

        # 3. Draw Summary Stats
        labels = [
            ("Tempo Total:", f"{stats['total_time']:.2f} s"),
            ("Velocidade Média:", f"{stats['avg_speed']:.1f} px/s"),
            ("Uso PID / Fuzzy:", f"{stats['pid_time']:.1f}s / {stats['fuzzy_time']:.1f}s"),
            ("Varredura BFS:", f"{stats['bfs_time']*1000:.2f} ms"),
            ("Roteamento A*:", f"{stats['astar_time']*1000:.2f} ms"),
            ("Erro Angular Médio:", f"{stats['mean_absolute_angle_error']:.2f}°")
        ]
        
        stat_y = panel_y + 115
        for lbl, val in labels:
            txt_lbl = self.font_medium.render(lbl, True, COLOR_TEXT_MUTED)
            txt_val = self.font_medium.render(val, True, COLOR_TEXT)
            
            surface.blit(txt_lbl, (panel_x + 50, stat_y))
            surface.blit(txt_val, (panel_x + panel_w - 50 - txt_val.get_width(), stat_y))
            stat_y += 32
            
        # 4. Buttons (Reiniciar & Gerar novo cenário)
        # Restart button
        restart_hover = self.btn_restart_rect.collidepoint(pygame.mouse.get_pos())
        restart_color = (40, 55, 75) if restart_hover else COLOR_BUTTON
        pygame.draw.rect(surface, restart_color, self.btn_restart_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_WALL_BORDER, self.btn_restart_rect, 1, border_radius=8)
        
        txt_restart = self.font_medium.render("Reiniciar", True, COLOR_TEXT)
        surface.blit(txt_restart, txt_restart.get_rect(center=self.btn_restart_rect.center))
        
        # New Scenario button
        new_hover = self.btn_new_rect.collidepoint(pygame.mouse.get_pos())
        new_color = (20, 110, 80) if new_hover else COLOR_START
        pygame.draw.rect(surface, new_color, self.btn_new_rect, border_radius=8)
        
        txt_new = self.font_medium.render("Novo Cenário", True, (255, 255, 255))
        surface.blit(txt_new, txt_new.get_rect(center=self.btn_new_rect.center))
