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
    
    pygame.init()
    pygame.display.set_caption("Simulador de Navegação Robótica 2D (PID vs Fuzzy)")
    
    cols = 19
    rows = 15
    cell_size = 40
    offset_y = 100

    width = cols * cell_size
    height = rows * cell_size + offset_y
    
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    map_obj = MazeMap(cols=cols, rows=rows, cell_size=cell_size, offset_y=offset_y)

    start_x, start_y = map_obj.grid_to_world(map_obj.start_grid[0], map_obj.start_grid[1])
    robot = Robot(start_x, start_y, theta=0.0)
    
    renderer = Renderer(width, height)
    
    game_state = 'SCANNING'

    bfs_results = {}
    astar_results = {}
    original_diamonds = []
    

    scan_index = 0
    scan_timer = 0
    scan_speed = 3  
    
    elapsed_sim_time = 0.0
    run_stats = {}
    plots_shown = False
    simulation_started = False

    def init_scenario(new_map=True):
        nonlocal game_state, bfs_results, astar_results, original_diamonds
        nonlocal scan_index, scan_timer, elapsed_sim_time, plots_shown, run_stats
        nonlocal simulation_started
        
        if new_map:
            map_obj.generate_maze()
            map_obj.spawn_diamonds()
            map_obj.create_obstacles()
        else:
            map_obj.diamonds = list(original_diamonds)
            map_obj.create_obstacles()
            

        original_diamonds = list(map_obj.diamonds)
        
        bfs_results = bfs_find_diamonds(map_obj.grid, map_obj.start_grid, map_obj.diamonds)
        
        robot.reset()
        elapsed_sim_time = 0.0
        plots_shown = False
        run_stats = {}
        simulation_started = False
        
        game_state = 'SCANNING'
        scan_index = 0
        scan_timer = 0

    init_scenario(new_map=True)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  
                    pos = event.pos
                    
                    if game_state == 'SIMULATION':
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
                        if renderer.btn_restart_rect.collidepoint(pos):
                            init_scenario(new_map=False)
                            print("[Simulador] Reiniciando mesmo cenário...")
                        elif renderer.btn_new_rect.collidepoint(pos):
                            init_scenario(new_map=True)
                            print("[Simulador] Gerando novo cenário...")

        if game_state == 'SCANNING':
            scan_timer += 1
            if scan_timer >= 1: 
                scan_timer = 0
                scan_index += scan_speed
                
            if scan_index >= len(bfs_results['visited_cells']):
                scan_index = len(bfs_results['visited_cells'])
                
                astar_results = calculate_optimal_route(
                    map_obj.grid, 
                    map_obj.start_grid, 
                    bfs_results['found_diamonds'], 
                    map_obj.end_grid
                )
                
                robot.set_path(astar_results['complete_path'], map_obj)
                
                print(f"[Busca] BFS varreu o mapa em {bfs_results['execution_time']*1000:.3f} ms.")
                print(f"[Busca] A* traçou a rota em {astar_results['execution_time']*1000:.3f} ms.")
                
                game_state = 'SIMULATION'

        elif game_state == 'SIMULATION':
            if simulation_started:
                elapsed_sim_time += dt
                
                robot.update(dt, map_obj, elapsed_sim_time)
                
                prev_collected = len(robot.diamonds_collected)
                current_collected = len(original_diamonds) - len(map_obj.diamonds)
                if current_collected > prev_collected:
                    if robot.diamonds_collected:
                        d_pos = robot.diamonds_collected[-1]
                        d_x, d_y = map_obj.grid_to_world(d_pos[0], d_pos[1])
                        renderer.add_collect_particles(d_x, d_y)
                        print(f"[Info] Diamante coletado em grid {d_pos}!")
            
            renderer.update_particles(dt)
            
            if robot.finished:
                game_state = 'COMPLETED'
                
                run_stats = TelemetryAnalyzer.analyze_run(
                    robot.telemetry, 
                    bfs_results['execution_time'], 
                    astar_results['execution_time']
                )
                
                TelemetryAnalyzer.print_summary(run_stats)

        elif game_state == 'COMPLETED':
            if not plots_shown:
                plots_shown = True
                print("[Info] Exibindo gráficos de telemetria...")
                show_performance_plots(robot.telemetry, run_stats)

        if game_state == 'SCANNING':
            renderer.draw_bfs_animation(screen, map_obj, bfs_results['visited_cells'], scan_index)
            
        elif game_state == 'SIMULATION':
            renderer.draw_grid(screen, map_obj)
            renderer.draw_path(screen, robot)
            renderer.draw_robot(screen, robot)
            renderer.draw_particles(screen)
            renderer.draw_hud(screen, robot, elapsed_sim_time, len(original_diamonds), simulation_started)
            
        elif game_state == 'COMPLETED':
            renderer.draw_grid(screen, map_obj)
            renderer.draw_path(screen, robot)
            renderer.draw_robot(screen, robot)
            renderer.draw_hud(screen, robot, elapsed_sim_time, len(original_diamonds), simulation_started)
            
            renderer.draw_completion_overlay(screen, run_stats)
            
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
