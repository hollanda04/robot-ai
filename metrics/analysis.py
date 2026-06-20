from typing import List, Dict, Any

class TelemetryAnalyzer:
    
    @staticmethod
    def analyze_run(
        telemetry: List[Dict[str, Any]], 
        bfs_time: float, 
        astar_time: float
    ) -> Dict[str, Any]:

        if not telemetry:
            return {
                'total_time': 0.0,
                'avg_speed': 0.0,
                'max_speed': 0.0,
                'pid_time': 0.0,
                'fuzzy_time': 0.0,
                'bfs_time': bfs_time,
                'astar_time': astar_time,
                'max_angle_error': 0.0,
                'mean_absolute_angle_error': 0.0
            }
            
        total_time = telemetry[-1]['time'] - telemetry[0]['time']
        
        speeds = [log['speed'] for log in telemetry]
        avg_speed = sum(speeds) / len(speeds)
        max_speed = max(speeds)
        
        pid_count = sum(1 for log in telemetry if log['controller'] == 'PID')
        fuzzy_count = sum(1 for log in telemetry if log['controller'] == 'Fuzzy')
        total_count = len(telemetry)
        
        pid_time = (pid_count / total_count) * total_time
        fuzzy_time = (fuzzy_count / total_count) * total_time

        angle_errors = [abs(log['angle_error_deg']) for log in telemetry]
        max_angle_error = max(angle_errors)
        mean_absolute_angle_error = sum(angle_errors) / len(angle_errors)
        
        return {
            'total_time': total_time,
            'avg_speed': avg_speed,
            'max_speed': max_speed,
            'pid_time': pid_time,
            'fuzzy_time': fuzzy_time,
            'bfs_time': bfs_time,
            'astar_time': astar_time,
            'max_angle_error': max_angle_error,
            'mean_absolute_angle_error': mean_absolute_angle_error
        }

    @staticmethod
    def print_summary(stats: Dict[str, Any]):
        print("\n" + "="*50)
        print("          RELATÓRIO DE DESEMPENHO DA IA          ")
        print("="*50)
        print(f"Tempo total de percurso:       {stats['total_time']:.2f} s")
        print(f"Velocidade média:              {stats['avg_speed']:.2f} px/s")
        print(f"Velocidade máxima:             {stats['max_speed']:.2f} px/s")
        print("-"*50)
        print("TEMPO GASTO POR CONTROLADOR:")
        print(f" - PID:                        {stats['pid_time']:.2f} s ({stats['pid_time']/stats['total_time']*100 if stats['total_time'] > 0 else 0:.1f}%)")
        print(f" - Lógica Fuzzy:               {stats['fuzzy_time']:.2f} s ({stats['fuzzy_time']/stats['total_time']*100 if stats['total_time'] > 0 else 0:.1f}%)")
        print("-"*50)
        print("TEMPO DE PROCESSAMENTO DOS ALGORITMOS DE BUSCA:")
        print(f" - BFS (Mapeamento/Busca):     {stats['bfs_time']*1000:.3f} ms")
        print(f" - A* (Roteamento Otimizado):  {stats['astar_time']*1000:.3f} ms")
        print("-"*50)
        print("PRECISÃO DO RASTREAMENTO DE WAYPOINTS:")
        print(f" - Erro angular máximo:        {stats['max_angle_error']:.2f}°")
        print(f" - Erro angular médio absoluto: {stats['mean_absolute_angle_error']:.2f}°")
        print("="*50 + "\n")
