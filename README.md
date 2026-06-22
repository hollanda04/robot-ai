# Simulador de Navegação Robótica 2D (PID vs Lógica Fuzzy)

Este é um simulador interativo bidimensional desenvolvido em Python com a biblioteca **Pygame**. O objetivo do simulador é demonstrar a navegação autônoma de um robô explorador por um labirinto gerado de forma procedural, coletando diamantes e alcançando um objetivo final através de algoritmos de roteamento de inteligência artificial e controle cinemático.

---

## 🚀 Funcionalidades Principais

* **Labirinto Procedural (`environment/`):** Geração dinâmica de mapas usando Busca em Profundidade (DFS) com aberturas de caminhos redundantes para simular rotas alternativas.
* **Varredura e Mapeamento (`search/bfs.py`):** O robô utiliza Busca em Largura (BFS) para descobrir a localização exata de diamantes espalhados aleatoriamente pelo mapa.
* **Roteamento Inteligente (`search/astar.py`):** Utiliza o algoritmo A* para calcular o caminho de menor custo, otimizando a ordem de visitação dos diamantes antes de seguir para a saída do labirinto (Mini-TSP).
* **Física e Colisão (`simulation/`):** Cinemática baseada no modelo de uniciclo com um sistema de resolução de colisões por deslizamento suave contra paredes.
* **Controle de Movimento Duplo (`control/`):**
  * **PID:** Controlador Proporcional-Integral-Derivativo convencional para rastreamento de ângulo e suavização de velocidade.
  * **Lógica Fuzzy:** Controlador baseado em inferência fuzzy de Sugeno (do zero em Python puro, mapeando pertinência de erro angular e distância do waypoint) atuando de forma suave nas curvas.
* **Telemetria Gráfica (`visualization/`):** Integração com **Matplotlib** para renderizar gráficos de desempenho comparativos (Trajetória Espacial, Velocidade Linear e Erro Angular ao longo do tempo).

---

## 🛠️ Dependências

O projeto utiliza poucas dependências externas. As bibliotecas necessárias são:

1. **Python 3.8+**
2. **Pygame** (renderização 2D e interface gráfica do jogo)
3. **Matplotlib** (geração de gráficos de telemetria)
4. **Numpy** (manipulação de vetores de dados nos plots)

---

## 📥 Instalação

Você pode instalar as dependências necessárias diretamente com o gerenciador de pacotes `pip`:

```bash
pip install -r requirements.txt
```

Ou usando o `uv` astral-sh/uv

```bash
uv sync`
```

---

## 🎮 Como Executar

Para iniciar o simulador, execute o arquivo `main.py` na raiz do diretório do projeto:

```bash
python main.py
```

ou

```bash
uv run main.py
```

### Passo a Passo de Uso:
1. **Varredura Inicial:** O cenário carregará e você verá uma animação em ciano cobrindo os caminhos explorados pelo algoritmo BFS.
2. **Aguardando Comando:** Assim que a varredura e o traçado de rota A* forem concluídos, o simulador pausará e exibirá **`AGUARDANDO...`** no HUD superior.
3. **Início do Trajeto:** Clique no botão **`PID Control`** ou **`Fuzzy Control`** no menu do topo para ligar os motores e iniciar o percurso.
4. **Alternância em Tempo Real:** Durante a corrida, clique nos botões do HUD a qualquer momento para alternar qual controlador guiará o robô. A linha do rastro pintará a cor correspondente (Amarelo para PID, Roxo para Fuzzy).
5. **Gráficos e Estatísticas:** Ao alcançar o ponto vermelho de saída (`E`), os gráficos de telemetria do Matplotlib serão abertos automaticamente. Feche a janela de gráficos para retornar ao painel de fim de jogo, onde poderá **Reiniciar** o circuito ou gerar um **Novo Cenário**.
