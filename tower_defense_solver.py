import heapq
import sys
import codecs
import tkinter as tk

def ler_arquivo(input_file):
    """Lê o arquivo de entrada e retorna o tabuleiro."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            n = int(f.readline().strip())
            board = [f.readline().strip() for _ in range(n)]
    except (UnicodeDecodeError, ValueError):
        try:
            with open(input_file, 'r', encoding='utf-16') as f:
                n = int(f.readline().strip())
                board = [f.readline().strip() for _ in range(n)]
        except (UnicodeDecodeError, ValueError):
            with open(input_file, 'rb') as f:
                raw_data = f.read()
                text = raw_data.decode('utf-16' if raw_data.startswith(codecs.BOM_UTF16) else 'utf-8', errors='ignore')
                lines = text.splitlines()
                n = int(lines[0].strip())
                board = [line.strip() for line in lines[1:n+1]]
    return n, board

def calcular_dano(board, n):
    """Calcula as posições das torres e o dano em cada célula."""
    # Encontra as posições das torres
    towers = [(i, j) for i in range(n) for j in range(n) if board[i][j] == 'T']
    
    # Calcula as células atacadas pelas torres
    attacked_cells = {}
    for i in range(n):
        for j in range(n):
            if board[i][j] != 'T':
                damage = sum(10 for tower_i, tower_j in towers 
                           if abs(i - tower_i) <= 1 and abs(j - tower_j) <= 1 and (i, j) != (tower_i, tower_j))
                if damage > 0:
                    attacked_cells[(i, j)] = damage
    
    return towers, attacked_cells

def solve_tower_defense(input_file, output_file):
    # Lê o arquivo de entrada
    n, board = ler_arquivo(input_file)
    
    # Calcula o dano
    _, attacked_cells = calcular_dano(board, n)
    
    # Direções possíveis: Sul, Norte, Leste, Oeste
    directions = [(1, 0, 'S'), (-1, 0, 'N'), (0, 1, 'L'), (0, -1, 'O')]
    
    # Algoritmo de Dijkstra
    start, end = (0, 0), (n-1, n-1)
    pq = [(0, start[0], start[1], "")]
    visited = set()
    
    while pq:
        damage, i, j, path = heapq.heappop(pq)
        
        if (i, j) == end:
            with open(output_file, 'w') as f:
                f.write(path)
            return path, damage
        
        if (i, j) in visited:
            continue
        
        visited.add((i, j))
        
        for di, dj, direction in directions:
            ni, nj = i + di, j + dj
            
            if 0 <= ni < n and 0 <= nj < n and board[ni][nj] != 'T' and (ni, nj) not in visited:
                new_damage = damage if (ni, nj) == end else damage + attacked_cells.get((ni, nj), 0)
                heapq.heappush(pq, (new_damage, ni, nj, path + direction))
    
    with open(output_file, 'w') as f:
        f.write("")
    return "", 0

def visualizar_solucao(input_file, output_file=None):
    """Visualiza graficamente a solução do problema."""
    # Configuração da janela
    root = tk.Tk()
    root.title("SOLUÇÃO IA TOWER DEFENSE")
    root.geometry("700x700")
    
    # Canvas e frames
    canvas = tk.Canvas(root, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    info_frame = tk.Frame(root)
    info_frame.pack(fill=tk.X, padx=20, pady=10)
    
    path_label = tk.Label(info_frame, text="Caminho: ", font=("Arial", 12))
    path_label.pack(anchor=tk.W)
    
    damage_label = tk.Label(info_frame, text="Dano Total: ", font=("Arial", 12))
    damage_label.pack(anchor=tk.W)
    
    # Legenda
    legend_frame = tk.Frame(root)
    legend_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Label(legend_frame, text="Legenda:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
    
    # Itens da legenda
    legendas = [
        ("Torre", "red", 1, 0), ("Início", "green", 1, 2),
        ("Fim", "blue", 2, 0), ("Caminho", "purple", 2, 2),
        ("Área de Dano (10)", "orange", 3, 0)
    ]
    
    for texto, cor, linha, coluna in legendas:
        tk.Frame(legend_frame, width=20, height=20, bg=cor).grid(row=linha, column=coluna, padx=5, pady=2)
        tk.Label(legend_frame, text=texto).grid(row=linha, column=coluna+1, sticky="w", 
                                               columnspan=3 if texto == "Área de Dano (10)" else 1)
    
    # Carregar o tabuleiro
    n, board = ler_arquivo(input_file)
    
    # Calcular dano
    towers, attacked_cells = calcular_dano(board, n)
    
    # Resolver o problema
    if output_file is None:
        output_file = "temp_solution.out"
    
    solution, total_damage = solve_tower_defense(input_file, output_file)
    
    # Atualizar as labels com os resultados
    path_label.config(text=f"Caminho: {solution}")
    damage_label.config(text=f"Dano Total: {total_damage}")
    
    # Funções de desenho
    def draw_board_and_path():
        canvas.delete("all")
        
        canvas_width = canvas.winfo_width() or 500
        canvas_height = canvas.winfo_height() or 500
        cell_size = min(canvas_width, canvas_height) // n
        
        # Desenhar áreas de dano
        for i in range(n):
            for j in range(n):
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                
                if (i, j) in attacked_cells:
                    canvas.create_rectangle(x1, y1, x2, y2, fill="orange", outline="")
        
        # Desenhar o tabuleiro
        for i in range(n):
            for j in range(n):
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                
                canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                
                if board[i][j] == 'T':
                    canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="black")
                    canvas.create_text(x1 + cell_size//2, y1 + cell_size//2, text="T", font=("Arial", 12, "bold"))
                elif (i, j) == (0, 0):
                    canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="black")
                elif (i, j) == (n-1, n-1):
                    canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="black")
                
                if (i, j) in attacked_cells:
                    canvas.create_text(x1 + cell_size//2, y1 + cell_size//2, 
                                      text=str(attacked_cells[(i, j)]), font=("Arial", 9))
        
        # Desenhar o caminho
        if solution:
            # Posição inicial
            i, j = 0, 0
            
            # Coordenadas do caminho
            path_coords = [(j * cell_size + cell_size//2, i * cell_size + cell_size//2)]
            path_cells = [(i, j)]
            
            # Seguir o caminho
            for direction in solution:
                if direction == 'S': i += 1
                elif direction == 'N': i -= 1
                elif direction == 'L': j += 1
                elif direction == 'O': j -= 1
                
                path_coords.append((j * cell_size + cell_size//2, i * cell_size + cell_size//2))
                path_cells.append((i, j))
            
            # Desenhar células do caminho
            for i, j in path_cells[1:-1]:
                x1, y1 = j * cell_size, i * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                canvas.create_rectangle(x1, y1, x2, y2, fill="purple", stipple="gray50")
            
            # Desenhar o caminho
            canvas.create_line(path_coords, fill="purple", width=3, arrow=tk.LAST)
    
    # Configurar o redimensionamento
    canvas.bind("<Configure>", lambda event: draw_board_and_path())
    
    # Desenhar inicialmente
    root.update()
    draw_board_and_path()
    
    # Iniciar o loop principal
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python tower_defense_solver.py instXX.in solXX.out")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    solution, total_damage = solve_tower_defense(input_file, output_file)
    print(f"Solução encontrada: {solution}")
    print(f"Dano total: {total_damage}")
    
    visualizar_solucao(input_file, output_file)
