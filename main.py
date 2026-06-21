"""
Main entry point for the 2D robot simulator.
Orchestrates Pygame initialization, game state transitions,
the execution of search algorithms (BFS and A*), controller selection,
and rendering loops.
"""

import sys
import pygame
from typing import Dict, Any

from environment.map import MazeMap
from simulation.robot import Robot
from search.bfs import bfs_find_diamonds
from search.astar import calculate_optimal_route
from metrics.analysis import TelemetryAnalyzer
from visualization.render import Renderer
from visualization.plots import show_performance_plots

# Game States
STATE_SCANNING = 'SCANNING'      # BFS visual animation
STATE_SIMULATION = 'SIMULATION'  # Robot navigating the route
STATE_COMPLETED = 'COMPLETED'    # Circuit finished


class Game:
    """
    Owns the simulation's state machine, core components, and main loop.
    Keeping this as a class (instead of nested closures + nonlocal) makes
    each state's behaviour independently readable and testable.
    """

    def __init__(
        self,
        cols: int = 19,
        rows: int = 15,
        cell_size: int = 40,
        offset_y: int = 100
    ):
        pygame.init()
        pygame.display.set_caption("Simulador de Navegação Robótica 2D (PID vs Fuzzy)")

        self.width = cols * cell_size
        self.height = rows * cell_size + offset_y

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        # Core components
        self.map_obj = MazeMap(cols=cols, rows=rows, cell_size=cell_size, offset_y=offset_y)
        start_x, start_y = self.map_obj.grid_to_world(*self.map_obj.start_grid)
        self.robot = Robot(start_x, start_y, theta=0.0)
        self.renderer = Renderer(self.width, self.height)

        # Search results
        self.bfs_results: Dict[str, Any] = {}
        self.astar_results: Dict[str, Any] = {}
        self.original_diamonds = []

        # Scanning animation state
        self.scan_index = 0
        self.scan_timer = 0
        self.scan_speed = 3  # cells scanned per frame

        # Simulation timing / stats
        self.elapsed_sim_time = 0.0
        self.run_stats: Dict[str, Any] = {}
        self.simulation_started = False

        self.game_state = STATE_SCANNING
        self.running = True

        self.init_scenario(new_map=True)

    # --- Scenario setup -------------------------------------------------

    def init_scenario(self, new_map: bool = True):
        """Initializes the environment, runs BFS discovery, and resets simulation variables."""
        if new_map:
            self.map_obj.generate_maze()
            self.map_obj.spawn_diamonds()
            self.map_obj.create_obstacles()
        else:
            # Recreate obstacles and restore diamonds to their original configuration
            self.map_obj.diamonds = list(self.original_diamonds)
            self.map_obj.create_obstacles()

        # Store original spawned diamonds before the robot starts collecting them
        self.original_diamonds = list(self.map_obj.diamonds)

        # Run BFS to locate all diamonds
        self.bfs_results = bfs_find_diamonds(
            self.map_obj.grid, self.map_obj.start_grid, self.map_obj.diamonds
        )

        # Reset robot and timings
        self.robot.reset()
        self.elapsed_sim_time = 0.0
        self.run_stats = {}
        self.simulation_started = False

        self.game_state = STATE_SCANNING
        self.scan_index = 0
        self.scan_timer = 0

    # --- Event handling ---------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

    def _handle_click(self, pos):
        if self.game_state == STATE_SIMULATION:
            self._handle_simulation_click(pos)
        elif self.game_state == STATE_COMPLETED:
            self._handle_completed_click(pos)

    def _handle_simulation_click(self, pos):
        renderer = self.renderer
        if renderer.btn_pid_rect.collidepoint(pos):
            self.robot.switch_controller('PID')
            self._announce_controller_start('controlador PID')
        elif renderer.btn_fuzzy_rect.collidepoint(pos):
            self.robot.switch_controller('Fuzzy')
            self._announce_controller_start('Lógica Fuzzy')

    def _announce_controller_start(self, label: str):
        if not self.simulation_started:
            self.simulation_started = True
            print(f"[Simulador] Iniciando percurso usando {label}.")
        else:
            print(f"[Controle] Alternado para {label}.")

    def _handle_completed_click(self, pos):
        renderer = self.renderer
        if renderer.btn_stats_rect.collidepoint(pos):
            # Telemetry plots are only ever shown on explicit user request
            print("[Info] Exibindo gráficos de telemetria...")
            show_performance_plots(self.robot.telemetry, self.run_stats)
        elif renderer.btn_restart_rect.collidepoint(pos):
            self.init_scenario(new_map=False)
            print("[Simulador] Reiniciando mesmo cenário...")
        elif renderer.btn_new_rect.collidepoint(pos):
            self.init_scenario(new_map=True)
            print("[Simulador] Gerando novo cenário...")

    # --- State updates ------------------------------------------------------

    def update(self, dt: float):
        if self.game_state == STATE_SCANNING:
            self._update_scanning()
        elif self.game_state == STATE_SIMULATION:
            self._update_simulation(dt)

    def _update_scanning(self):
        """Advances the visual BFS scanning expansion; transitions to SIMULATION once done."""
        self.scan_timer += 1
        if self.scan_timer >= 1:
            self.scan_timer = 0
            self.scan_index += self.scan_speed

        visited_cells = self.bfs_results['visited_cells']
        if self.scan_index >= len(visited_cells):
            self.scan_index = len(visited_cells)
            self._compute_route_and_start_simulation()

    def _compute_route_and_start_simulation(self):
        self.astar_results = calculate_optimal_route(
            self.map_obj.grid,
            self.map_obj.start_grid,
            self.bfs_results['found_diamonds'],
            self.map_obj.end_grid
        )
        self.robot.set_path(self.astar_results['complete_path'], self.map_obj)

        print(f"[Busca] BFS varreu o mapa em {self.bfs_results['execution_time']*1000:.3f} ms.")
        print(f"[Busca] A* traçou a rota em {self.astar_results['execution_time']*1000:.3f} ms.")

        self.game_state = STATE_SIMULATION

    def _update_simulation(self, dt: float):
        if self.simulation_started:
            self.elapsed_sim_time += dt
            prev_collected = len(self.robot.diamonds_collected)

            self.robot.update(dt, self.map_obj, self.elapsed_sim_time)

            # If the number of collected diamonds increased, trigger a visual burst
            current_collected = len(self.original_diamonds) - len(self.map_obj.diamonds)
            if current_collected > prev_collected and self.robot.diamonds_collected:
                d_pos = self.robot.diamonds_collected[-1]
                d_x, d_y = self.map_obj.grid_to_world(*d_pos)
                self.renderer.add_collect_particles(d_x, d_y)
                print(f"[Info] Diamante coletado em grid {d_pos}!")

        # Particle animations update regardless of whether the robot is moving
        self.renderer.update_particles(dt)

        if self.robot.finished:
            self._finish_run()

    def _finish_run(self):
        self.game_state = STATE_COMPLETED
        self.run_stats = TelemetryAnalyzer.analyze_run(
            self.robot.telemetry,
            self.bfs_results['execution_time'],
            self.astar_results['execution_time']
        )
        TelemetryAnalyzer.print_summary(self.run_stats)

    # --- Rendering ------------------------------------------------------

    def render(self):
        if self.game_state == STATE_SCANNING:
            self.renderer.draw_bfs_animation(
                self.screen, self.map_obj, self.bfs_results['visited_cells'], self.scan_index
            )
        elif self.game_state == STATE_SIMULATION:
            self._render_world()
            self.renderer.draw_particles(self.screen)
            self.renderer.draw_hud(
                self.screen, self.robot, self.elapsed_sim_time,
                len(self.original_diamonds), self.simulation_started
            )
        elif self.game_state == STATE_COMPLETED:
            self._render_world()
            self.renderer.draw_hud(
                self.screen, self.robot, self.elapsed_sim_time,
                len(self.original_diamonds), self.simulation_started
            )
            self.renderer.draw_completion_overlay(self.screen, self.run_stats)

        pygame.display.flip()

    def _render_world(self):
        """Shared background rendering used by both SIMULATION and COMPLETED states."""
        self.renderer.draw_grid(self.screen, self.map_obj)
        self.renderer.draw_path(self.screen, self.robot)
        self.renderer.draw_robot(self.screen, self.robot)

    # --- Main loop ------------------------------------------------------

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()


def main():
    game = Game(cols=19, rows=15, cell_size=40, offset_y=100)
    game.run()
    sys.exit()


if __name__ == '__main__':
    main()