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

def main():
    # 1. Setup Pygame Window
    pygame.init()
    pygame.display.set_caption("Simulador de Navegação Robótica 2D (PID vs Fuzzy)")
    
    # Maze Dimensions
    cols = 19
    rows = 15
    cell_size = 40
    offset_y = 100
    
    # Window dimensions
    width = cols * cell_size
    height = rows * cell_size + offset_y
    
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    
    # 2. Instantiate core components
    map_obj = MazeMap(cols=cols, rows=rows, cell_size=cell_size, offset_y=offset_y)
    
    # Spawn robot at the start position (world coordinates)
    start_x, start_y = map_obj.grid_to_world(map_obj.start_grid[0], map_obj.start_grid[1])
    robot = Robot(start_x, start_y, theta=0.0)
    
    renderer = Renderer(width, height)
    
    # Game States: 'SCANNING' (BFS visual animation), 'SIMULATION' (Running), 'COMPLETED' (Finished circuit)
    game_state = 'SCANNING'
    
    # BFS and A* Routing variables
    bfs_results = {}
    astar_results = {}
    original_diamonds = []
    
    # Scanning animation states
    scan_index = 0
    scan_timer = 0
    scan_speed = 3  # cells scanned per frame
    
    # Simulation timing
    elapsed_sim_time = 0.0
    run_stats = {}
    plots_shown = False
    simulation_started = False

    def init_scenario(new_map=True):
        """Initializes the environment, runs BFS discovery, and resets simulation variables."""
        nonlocal game_state, bfs_results, astar_results, original_diamonds
        nonlocal scan_index, scan_timer, elapsed_sim_time, plots_shown, run_stats
        nonlocal simulation_started
        
        if new_map:
            # Generate new map structure
            map_obj.generate_maze()
            map_obj.spawn_diamonds()
            map_obj.create_obstacles()
        else:
            # Recreate obstacles and restore diamonds to their original configurations
            map_obj.diamonds = list(original_diamonds)
            map_obj.create_obstacles()
            
        # Store original spawned diamonds before robot starts collecting them
        original_diamonds = list(map_obj.diamonds)
        
        # Run BFS to locate all diamonds
        bfs_results = bfs_find_diamonds(map_obj.grid, map_obj.start_grid, map_obj.diamonds)
        
        # Reset robot and timings
        robot.reset()
        elapsed_sim_time = 0.0
        plots_shown = False
        run_stats = {}
        simulation_started = False
        
        # Start in SCANNING mode
        game_state = 'SCANNING'
        scan_index = 0
        scan_timer = 0

    # Initialize the first scenario
    init_scenario(new_map=True)

    # Main Game Loop
    running = True
    while running:
        # Get dt (time step) in seconds
        # Limit frame rate to 60 FPS
        dt = clock.tick(60) / 1000.0
        
        # --- 1. Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click
                    pos = event.pos
                    
                    if game_state == 'SIMULATION':
                        # Check HUD controller switches
                        if renderer.btn_pid_rect.collidepoint(pos):
                            robot.switch_controller('PID')
                            if not simulation_started:
                                simulation_started = True
                                print("[Simulador] Iniciando percurso usando controlador PID.")
                            else:
                                print("[Controle] Alternado para PID.")
                        elif renderer.btn_fuzzy_rect.collidepoint(pos):
                            robot.switch_controller('Fuzzy')
                            if not simulation_started:
                                simulation_started = True
                                print("[Simulador] Iniciando percurso usando Lógica Fuzzy.")
                            else:
                                print("[Controle] Alternado para Lógica Fuzzy.")
                            
                    elif game_state == 'COMPLETED':
                        # Check restart/new scenario buttons
                        if renderer.btn_restart_rect.collidepoint(pos):
                            # Restart current scenario
                            init_scenario(new_map=False)
                            print("[Simulador] Reiniciando mesmo cenário...")
                        elif renderer.btn_new_rect.collidepoint(pos):
                            # Generate new scenario
                            init_scenario(new_map=True)
                            print("[Simulador] Gerando novo cenário...")

        # --- 2. State Update ---
        if game_state == 'SCANNING':
            # Run visual BFS scanning expansion
            scan_timer += 1
            if scan_timer >= 1: # update cells
                scan_timer = 0
                scan_index += scan_speed
                
            # If visual scan is complete, calculate A* routing and transition to simulation
            if scan_index >= len(bfs_results['visited_cells']):
                scan_index = len(bfs_results['visited_cells'])
                
                # Compute A* optimal route visiting found diamonds in best sequence
                astar_results = calculate_optimal_route(
                    map_obj.grid, 
                    map_obj.start_grid, 
                    bfs_results['found_diamonds'], 
                    map_obj.end_grid
                )
                
                # Load path into robot
                robot.set_path(astar_results['complete_path'], map_obj)
                
                print(f"[Busca] BFS varreu o mapa em {bfs_results['execution_time']*1000:.3f} ms.")
                print(f"[Busca] A* traçou a rota em {astar_results['execution_time']*1000:.3f} ms.")
                
                game_state = 'SIMULATION'

        elif game_state == 'SIMULATION':
            if simulation_started:
                # Update elapsed simulator time
                elapsed_sim_time += dt
                
                # Update robot kinematics, controls, and collections
                robot.update(dt, map_obj, elapsed_sim_time)
                
                # Check for particle animations
                # If the number of collected diamonds increased, trigger a visual diamond burst
                prev_collected = len(robot.diamonds_collected)
                # Robot update may have modified map_obj.diamonds length
                current_collected = len(original_diamonds) - len(map_obj.diamonds)
                if current_collected > prev_collected:
                    # Add particles at the most recently collected diamond position
                    if robot.diamonds_collected:
                        d_pos = robot.diamonds_collected[-1]
                        d_x, d_y = map_obj.grid_to_world(d_pos[0], d_pos[1])
                        renderer.add_collect_particles(d_x, d_y)
                        print(f"[Info] Diamante coletado em grid {d_pos}!")
            
            # Particles and rendering animations can update regardless of movement
            renderer.update_particles(dt)
            
            # Check if robot has completed the circuit (reached the End)
            if robot.finished:
                game_state = 'COMPLETED'
                
                # Compile final run statistics
                run_stats = TelemetryAnalyzer.analyze_run(
                    robot.telemetry, 
                    bfs_results['execution_time'], 
                    astar_results['execution_time']
                )
                
                # Output to console
                TelemetryAnalyzer.print_summary(run_stats)

        elif game_state == 'COMPLETED':
            # Handle plots display once
            if not plots_shown:
                plots_shown = True
                print("[Info] Exibindo gráficos de telemetria...")
                show_performance_plots(robot.telemetry, run_stats)

        # --- 3. Rendering ---
        if game_state == 'SCANNING':
            # Render BFS expansion scanning animation
            renderer.draw_bfs_animation(screen, map_obj, bfs_results['visited_cells'], scan_index)
            
        elif game_state == 'SIMULATION':
            # Standard simulation rendering
            renderer.draw_grid(screen, map_obj)
            renderer.draw_path(screen, robot)
            renderer.draw_robot(screen, robot)
            renderer.draw_particles(screen)
            renderer.draw_hud(screen, robot, elapsed_sim_time, len(original_diamonds), simulation_started)
            
        elif game_state == 'COMPLETED':
            # Standard background under overlay
            renderer.draw_grid(screen, map_obj)
            renderer.draw_path(screen, robot)
            renderer.draw_robot(screen, robot)
            renderer.draw_hud(screen, robot, elapsed_sim_time, len(original_diamonds), simulation_started)
            
            # Draw the game over completion panel
            renderer.draw_completion_overlay(screen, run_stats)
            
        # Swap buffers
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
