import heapq
import sys
import codecs
import tkinter as tk

def ler_arquivo(arquivo_entrada):
    """Lê o arquivo de entrada e retorna o tabuleiro."""
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f:
            n = int(f.readline().strip())
            tabuleiro = [f.readline().strip() for _ in range(n)]
    except (UnicodeDecodeError, ValueError):
        try:
            with open(arquivo_entrada, 'r', encoding='utf-16') as f:
                n = int(f.readline().strip())
                tabuleiro = [f.readline().strip() for _ in range(n)]
        except (UnicodeDecodeError, ValueError):
            with open(arquivo_entrada, 'rb') as f:
                dados_brutos = f.read()
                texto = dados_brutos.decode('utf-16' if dados_brutos.startswith(codecs.BOM_UTF16) else 'utf-8', errors='ignore')
                linhas = texto.splitlines()
                n = int(linhas[0].strip())
                tabuleiro = [linha.strip() for linha in linhas[1:n+1]]
    return n, tabuleiro

def calcular_dano(tabuleiro, n):
    """Calcula as posições das torres e o dano em cada célula."""
    # Encontra as posições das torres
    torres = [(i, j) for i in range(n) for j in range(n) if tabuleiro[i][j] == 'T']
    
    # Calcula as células atacadas pelas torres
    celulas_atacadas = {}
    for i in range(n):
        for j in range(n):
            if tabuleiro[i][j] != 'T':
                dano = sum(10 for torre_i, torre_j in torres 
                           if abs(i - torre_i) <= 1 and abs(j - torre_j) <= 1 and (i, j) != (torre_i, torre_j))
                if dano > 0:
                    celulas_atacadas[(i, j)] = dano
    
    return torres, celulas_atacadas

def resolver_tower_defense(arquivo_entrada, arquivo_saida):
    # Lê o arquivo de entrada
    n, tabuleiro = ler_arquivo(arquivo_entrada)
    
    # Calcula o dano
    _, celulas_atacadas = calcular_dano(tabuleiro, n)
    
    # Direções possíveis: Sul, Norte, Leste, Oeste
    direcoes = [(1, 0, 'S'), (-1, 0, 'N'), (0, 1, 'L'), (0, -1, 'O')]
    
    # Algoritmo de Dijkstra
    inicio, fim = (0, 0), (n-1, n-1)
    fila_prioridade = [(0, inicio[0], inicio[1], "")]
    visitados = set()
    
    while fila_prioridade:
        dano, i, j, caminho = heapq.heappop(fila_prioridade)
        
        if (i, j) == fim:
            with open(arquivo_saida, 'w') as f:
                f.write(caminho)
            return caminho, dano
        
        if (i, j) in visitados:
            continue
        
        visitados.add((i, j))
        
        for di, dj, direcao in direcoes:
            ni, nj = i + di, j + dj
            
            if 0 <= ni < n and 0 <= nj < n and tabuleiro[ni][nj] != 'T' and (ni, nj) not in visitados:
                novo_dano = dano if (ni, nj) == fim else dano + celulas_atacadas.get((ni, nj), 0)
                heapq.heappush(fila_prioridade, (novo_dano, ni, nj, caminho + direcao))
    
    with open(arquivo_saida, 'w') as f:
        f.write("")
    return "", 0

def visualizar_solucao(arquivo_entrada, arquivo_saida=None):
    """Visualiza graficamente a solução do problema."""
    # Configuração da janela
    raiz = tk.Tk()
    raiz.title("SOLUÇÃO IA TOWER DEFENSE")
    raiz.geometry("700x700")
    
    # Canvas e frames
    canvas = tk.Canvas(raiz, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    frame_info = tk.Frame(raiz)
    frame_info.pack(fill=tk.X, padx=20, pady=10)
    
    rotulo_caminho = tk.Label(frame_info, text="Caminho: ", font=("Arial", 12))
    rotulo_caminho.pack(anchor=tk.W)
    
    rotulo_dano = tk.Label(frame_info, text="Dano Total: ", font=("Arial", 12))
    rotulo_dano.pack(anchor=tk.W)
    
    # Legenda
    frame_legenda = tk.Frame(raiz)
    frame_legenda.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Label(frame_legenda, text="Legenda:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
    
    # Itens da legenda
    legendas = [
        ("Torre", "red", 1, 0), ("Início", "green", 1, 2),
        ("Fim", "blue", 2, 0), ("Caminho", "purple", 2, 2),
        ("Área de Dano (10)", "orange", 3, 0)
    ]
    
    for texto, cor, linha, coluna in legendas:
        tk.Frame(frame_legenda, width=20, height=20, bg=cor).grid(row=linha, column=coluna, padx=5, pady=2)
        tk.Label(frame_legenda, text=texto).grid(row=linha, column=coluna+1, sticky="w", 
                                               columnspan=3 if texto == "Área de Dano (10)" else 1)
    
    # Carregar o tabuleiro
    n, tabuleiro = ler_arquivo(arquivo_entrada)
    
    # Calcular dano
    torres, celulas_atacadas = calcular_dano(tabuleiro, n)
    
    # Resolver o problema
    if arquivo_saida is None:
        arquivo_saida = "temp_solution.out"
    
    solucao, dano_total = resolver_tower_defense(arquivo_entrada, arquivo_saida)
    
    # Atualizar as labels com os resultados
    rotulo_caminho.config(text=f"Caminho: {solucao}")
    rotulo_dano.config(text=f"Dano Total: {dano_total}")
    
    # Funções de desenho
    def desenhar_tabuleiro_e_caminho():
        canvas.delete("all")
        
        largura_canvas = canvas.winfo_width() or 500
        altura_canvas = canvas.winfo_height() or 500
        tamanho_celula = min(largura_canvas, altura_canvas) // n
        
        # Desenhar áreas de dano
        for i in range(n):
            for j in range(n):
                x1, y1 = j * tamanho_celula, i * tamanho_celula
                x2, y2 = x1 + tamanho_celula, y1 + tamanho_celula
                
                if (i, j) in celulas_atacadas:
                    canvas.create_rectangle(x1, y1, x2, y2, fill="orange", outline="")
        
        # Desenhar o tabuleiro
        for i in range(n):
            for j in range(n):
                x1, y1 = j * tamanho_celula, i * tamanho_celula
                x2, y2 = x1 + tamanho_celula, y1 + tamanho_celula
                
                canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                
                if tabuleiro[i][j] == 'T':
                    canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="black")
                    canvas.create_text(x1 + tamanho_celula//2, y1 + tamanho_celula//2, text="T", font=("Arial", 12, "bold"))
                elif (i, j) == (0, 0):
                    canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="black")
                elif (i, j) == (n-1, n-1):
                    canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="black")
                
                if (i, j) in celulas_atacadas:
                    canvas.create_text(x1 + tamanho_celula//2, y1 + tamanho_celula//2, 
                                      text=str(celulas_atacadas[(i, j)]), font=("Arial", 9))
        
        # Desenhar o caminho
        if solucao:
            # Posição inicial
            i, j = 0, 0
            
            # Coordenadas do caminho
            coords_caminho = [(j * tamanho_celula + tamanho_celula//2, i * tamanho_celula + tamanho_celula//2)]
            celulas_caminho = [(i, j)]
            
            # Seguir o caminho
            for direcao in solucao:
                if direcao == 'S': i += 1
                elif direcao == 'N': i -= 1
                elif direcao == 'L': j += 1
                elif direcao == 'O': j -= 1
                
                coords_caminho.append((j * tamanho_celula + tamanho_celula//2, i * tamanho_celula + tamanho_celula//2))
                celulas_caminho.append((i, j))
            
            # Desenhar células do caminho
            for i, j in celulas_caminho[1:-1]:
                x1, y1 = j * tamanho_celula, i * tamanho_celula
                x2, y2 = x1 + tamanho_celula, y1 + tamanho_celula
                canvas.create_rectangle(x1, y1, x2, y2, fill="purple", stipple="gray50")
            
            # Desenhar o caminho
            canvas.create_line(coords_caminho, fill="purple", width=3, arrow=tk.LAST)
    
    # Configurar o redimensionamento
    canvas.bind("<Configure>", lambda evento: desenhar_tabuleiro_e_caminho())
    
    # Desenhar inicialmente
    raiz.update()
    desenhar_tabuleiro_e_caminho()
    
    # Iniciar o loop principal
    raiz.mainloop()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python tower_defense_solver.py instXX.in solXX.out")
        sys.exit(1)
    
    arquivo_entrada = sys.argv[1]
    arquivo_saida = sys.argv[2]
    
    solucao, dano_total = resolver_tower_defense(arquivo_entrada, arquivo_saida)
    print(f"Solução encontrada: {solucao}")
    print(f"Dano total: {dano_total}")
    
    visualizar_solucao(arquivo_entrada, arquivo_saida)
