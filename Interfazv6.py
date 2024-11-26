import csv
import tkinter as tk
from tkinter import ttk, messagebox
import random

class SmartHorsesGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Horses")

        # Variables
        self.levels = ["Principiante", "Amateur", "Experto"]
        self.selected_level = tk.StringVar(value=self.levels[0])
        self.selected_level_ia = tk.StringVar(value=self.levels[0])
        self.game_mode = tk.StringVar(value="vs Humano")
        self.points_positions = {}
        self.x2_positions = set()
        self.white_horse = None
        self.black_horse = None
        self.white_points = tk.IntVar(value=0)
        self.black_points = tk.IntVar(value=0)
        self.turn = tk.StringVar(value="Turno: Caballo Blanco")
        self.white_x2 = False
        self.black_x2 = False
        self.move_history = set()  # Evitar ciclos
        self.game_history = []  # Almacenar partidas

        # Frames
        self.setup_ui()

    def setup_ui(self):
        # Frame para selección de nivel y modo
        level_frame = ttk.LabelFrame(self.root, text="Configuración del Juego")
        level_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(level_frame, text="Modo de Juego:").grid(row=0, column=0, padx=5, pady=5)
        self.game_mode = tk.StringVar(value="vs Humano")
        mode_menu = ttk.OptionMenu(level_frame, self.game_mode, "vs Humano", "vs IA", command=self.toggle_ia_level)
        mode_menu.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(level_frame, text="Selecciona el nivel de dificultad IA:").grid(row=1, column=0, padx=5, pady=5)
        self.selected_level_ia = tk.StringVar(value=self.levels[0])
        self.levelia_menu = ttk.OptionMenu(level_frame, self.selected_level_ia, *self.levels)
        self.levelia_menu.grid(row=1, column=1, padx=5, pady=5)

        # Inicialmente ocultar el nivel de dificultad IA
        self.levelia_menu.grid_remove()
        ttk.Label(level_frame, text="Selecciona el nivel de dificultad IA:").grid_remove()

        ttk.Label(level_frame, text="Selecciona el nivel de dificultad:").grid(row=2, column=0, padx=5, pady=5)
        self.selected_level = tk.StringVar(value=self.levels[0])
        level_menu = ttk.OptionMenu(level_frame, self.selected_level, *self.levels)
        level_menu.grid(row=2, column=1, padx=5, pady=5)

        # Botón para iniciar el juego
        start_button = ttk.Button(level_frame, text="Iniciar Juego", command=self.start_game)
        start_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Tablero
        self.board_frame = ttk.Frame(self.root)
        self.board_frame.pack(pady=10, padx=10)
        self.board_buttons = []

        for i in range(8):
            row = []
            for j in range(8):
                button = tk.Button(
                    self.board_frame,
                    text="", width=6, height=3,
                    state=tk.DISABLED,
                    relief=tk.RIDGE,
                    command=self.create_move_command(i, j)
                )
                button.grid(row=i, column=j, padx=2, pady=2)
                row.append(button)
            self.board_buttons.append(row)

        # Información del juego
        self.info_frame = ttk.LabelFrame(self.root, text="Información del Juego")
        self.info_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(self.info_frame, text="Puntos Caballo Blanco:").grid(row=0, column=0, sticky="e", padx=5)
        ttk.Label(self.info_frame, textvariable=self.white_points).grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(self.info_frame, text="Puntos Caballo Negro:").grid(row=1, column=0, sticky="e", padx=5)
        ttk.Label(self.info_frame, textvariable=self.black_points).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(self.info_frame, textvariable=self.turn).grid(row=2, column=0, columnspan=2, pady=5)


    def toggle_ia_level(self, mode):
        """Muestra u oculta el nivel de IA dependiendo del modo de juego seleccionado."""
        if mode == "vs IA":
            self.levelia_menu.grid()
            ttk.Label(self.root, text="Selecciona el nivel de dificultad IA:").grid()
        else:
            self.levelia_menu.grid_remove()
            ttk.Label(self.root, text="Selecciona el nivel de dificultad IA:").grid_remove()


    def create_move_command(self, x, y):
        return lambda: self.move_black_horse(x, y)

    def start_game(self):
        self.reset_scores()
        self.initialize_positions()
        self.update_board()
        self.enable_board()
        self.root.after(500, self.move_white_horse)

    def reset_scores(self):
        self.white_points.set(0)
        self.black_points.set(0)

    def initialize_positions(self):
        # Reset tablero
        for row in self.board_buttons:
            for button in row:
                button.config(text="", state=tk.DISABLED, bg="SystemButtonFace")

        # Generar posiciones aleatorias
        positions = random.sample(range(64), 16)
        self.points_positions = {pos: i + 1 for i, pos in enumerate(positions[:10])}
        self.x2_positions = set(positions[10:14])
        for x2_pos in self.x2_positions:
            self.points_positions[x2_pos] = 11
        self.white_horse = positions[14]
        self.black_horse = positions[15]
    def collect_points(self, pos, player):
        """Recoge los puntos de una casilla para un jugador."""
        multiplier = 2 if (player == "white" and self.white_x2) or (player == "black" and self.black_x2) else 1
        if pos in self.points_positions:
            points = self.points_positions.pop(pos) * multiplier
            if player == "white":
                self.white_points.set(self.white_points.get() + points)
                self.white_x2 = False
            elif player == "black":
                self.black_points.set(self.black_points.get() + points)
                self.black_x2 = False

        if pos in self.x2_positions:
            if player == "white":
                self.white_x2 = True
            elif player == "black":
                self.black_x2 = True
            self.x2_positions.remove(pos)    
    def print_horses_positions(self):
        """Imprime en la terminal las posiciones actuales de los caballos."""
        white_x, white_y = divmod(self.white_horse, 8)
        black_x, black_y = divmod(self.black_horse, 8)
        print(f"Caballo Blanco: Fila {white_x + 1}, Columna {white_y + 1}")
        print(f"Caballo Negro: Fila {black_x + 1}, Columna {black_y + 1}")
        return white_x, white_y

    def update_board(self):
        # Limpiar tablero
        for row in self.board_buttons:
            for button in row:
                button.config(text="", bg="SystemButtonFace")

        # Actualizar casillas con puntos
        for pos, points in self.points_positions.items():
            x, y = divmod(pos, 8)
            self.board_buttons[x][y].config(text=str(points), bg="lightblue")

        # Actualizar casillas x2
        for pos in self.x2_positions:
            x, y = divmod(pos, 8)
            self.board_buttons[x][y].config(text="x2", bg="yellow")

        # Actualizar caballos
        wx, wy = divmod(self.white_horse, 8)
        self.board_buttons[wx][wy].config(text="♞", bg="white", state=tk.NORMAL)

        bx, by = divmod(self.black_horse, 8)
        self.board_buttons[bx][by].config(text="♘", bg="black", fg="black", state=tk.NORMAL)

    def enable_board(self):
        """Habilitar las casillas para el movimiento del caballo negro."""
        for row in self.board_buttons:
            for button in row:
                button.config(state=tk.NORMAL)
    def get_valid_moves(self, pos):
        """Devuelve una lista de movimientos válidos en 'L' para una posición."""
        x, y = divmod(pos, 8)
        
        moves = [
            (x + 2, y + 1), (x + 2, y - 1), (x - 2, y + 1), (x - 2, y - 1),
            (x + 1, y + 2), (x + 1, y - 2), (x - 1, y + 2), (x - 1, y - 2)
        ]
        print(moves)
        return [nx * 8 + ny for nx, ny in moves if 0 <= nx < 8 and 0 <= ny < 8]
    def is_valid_move(self, current_pos, new_pos):
        """Verifica si un movimiento es válido en 'L'."""
        return new_pos in self.get_valid_moves(current_pos)
    def minimax(self, pos, depth, maximizing_player, alpha, beta,ia=False):
        if depth == 0 or not self.points_positions:
            return self.evaluate_board_white(pos, maximizing_player) if  not ia else  self.evaluate_board_black(pos, maximizing_player)

        valid_moves = self.get_valid_moves(pos)
        valid_moves = [m for m in valid_moves if m not in self.move_history]  # Evitar ciclos

        if maximizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
                self.move_history.add(move)
                eval = self.minimax(move, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval)
                self.move_history.remove(move)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                self.move_history.add(move)
                eval = self.minimax(move, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)
                self.move_history.remove(move)
                if beta <= alpha:
                    break
            return min_eval
        
    def evaluate_board_white(self, pos, maximizing_player):
        """
        Evalúa el estado del tablero para el caballo blanco.
        Prioriza casillas con multiplicador x2, luego puntos, y evita ciclos.
        """

        # Penalización alta si la posición ya está en el historial de movimientos
        cycle_penalty = -1000 if pos in self.move_history else 0

        # Puntos inmediatos
        points = self.points_positions.get(pos, 0)

        # Multiplicador x2
        multiplier = 2 if pos in self.x2_positions else 1

        # Movimientos futuros válidos
        future_moves = len([m for m in self.get_valid_moves(pos) if m not in self.move_history])

        # Heurística ajustada para el jugador maximizador o minimizador
        if maximizing_player:
            # Maximizar puntos y x2
            score = (
                points * multiplier * 10  # Puntos x2 altamente priorizados
                + future_moves * 0.5  # Valora opciones futuras
                + cycle_penalty  # Penalización por ciclos
            )
        else:
            # Minimizar ventajas del oponente
            score = (
                points * multiplier * -10  # Penaliza puntos y x2
                - future_moves * 0.5  # Penaliza opciones futuras
                + cycle_penalty  # Penalización por ciclos
            )

        return score




    
    def evaluate_board_black(self, pos, maximizing_player):
        """
        Heurística basada en el control del centro y la restricción del oponente.
        """
        # Posición del caballo contrario
        opponent_horse = self.black_horse if maximizing_player else self.white_horse
        
        # Restricción de movimientos del oponente
        opponent_moves = self.get_valid_moves(opponent_horse)
        restricted_opponent_moves = len(opponent_moves)
        
        # Control del centro del tablero (valores más altos en posiciones centrales)
        x, y = divmod(pos, 8)
        center_score = max(0, 4 - abs(x - 3.5)) + max(0, 4 - abs(y - 3.5))
        
        # Puntos en la casilla actual
        points = self.points_positions.get(pos, 0)
        multiplier = 2 if pos in self.x2_positions else 1
        point_score = points * multiplier
        
        # Fórmula de la heurística
        score = (
            center_score * 1.5  # Favorece posiciones centrales
            - restricted_opponent_moves * 0.7  # Penaliza dejar opciones al oponente
            + point_score * 1  # Valora puntos en la casilla actual
        )
        
        return score
    
    def move_white_horse(self):
        """Mueve el caballo blanco usando Minimax."""
        if self.turn.get() != "Turno: Caballo Blanco":
            return

        depth = {"Principiante": 2, "Amateur": 4, "Experto": 6}[self.selected_level.get()]
        valid_moves = self.get_valid_moves(self.white_horse)
        if not valid_moves:
            self.turn.set("Turno: Caballo Negro")
            return

        best_move = None
        best_score = float('-inf')

        for move in valid_moves:
            self.move_history.add(move)  # Añadir a historial para evitar ciclos
            points = self.points_positions.get(move, 0)
            multiplier = 2 if move in self.x2_positions else 1
            move_score = self.minimax(move, depth - 1, False, float('-inf'), float('inf')) + points * multiplier
            self.move_history.remove(move)  # Limpiar historial

            if move_score > best_score:
                best_score = move_score
                best_move = move

        if best_move is not None:
            self.collect_points(best_move, "white")
            self.white_horse = best_move
            if self.game_mode.get() == "vs IA":
                self.root.after(500, self.move_black_ia)
            

        self.turn.set("Turno: Caballo Negro")
        self.update_board()
        self.check_game_end()
        self.print_horses_positions()
    def move_black_horse(self, x, y):
        """Mueve el caballo negro a la posición seleccionada."""
        if self.turn.get() != "Turno: Caballo Negro":
            return

        pos = x * 8 + y
        if self.is_valid_move(self.black_horse, pos):
            self.collect_points(pos, "black")
            self.black_horse = pos
            self.turn.set("Turno: Caballo Blanco")
            self.update_board()
            self.check_game_end()
            if self.game_mode.get() == "vs IA":
                self.root.after(500, self.move_black_ia)
            else:
                self.root.after(500, self.move_white_horse)    

    def move_black_ia(self):
        """Mueve el caballo negro usando Minimax."""
        depth = {"Principiante": 2, "Amateur": 4, "Experto": 6}[self.selected_level_ia.get()]
        valid_moves = self.get_valid_moves(self.black_horse)
        if not valid_moves:
            self.turn.set("Turno: Caballo Blanco")
            return

        best_move = None
        best_score = float('-inf')

        for move in valid_moves:
            self.move_history.add(move)
            points = self.points_positions.get(move, 0)
            multiplier = 2 if move in self.x2_positions else 1
            move_score = self.minimax(move, depth - 1, False, float('-inf'), float('inf'),ia=True) + points * multiplier
            self.move_history.remove(move)

            if move_score > best_score:
                best_score = move_score
                best_move = move

        if best_move is not None:
            self.collect_points(best_move, "black")
            self.black_horse = best_move

        self.turn.set("Turno: Caballo Blanco")
        self.update_board()
        self.check_game_end()
        self.root.after(500, self.move_white_horse) 

    def check_game_end(self):
        """Verifica si el juego ha terminado."""
        if not self.points_positions:
            winner = "Empate"
            if self.white_points.get() > self.black_points.get():
                winner = "Caballo Blanco"
            elif self.black_points.get() > self.white_points.get():
                winner = "Caballo Negro"
            self.save_game_record(winner)
            messagebox.showinfo("Juego Terminado", f"¡El juego ha terminado! Ganador: {winner}")
            self.root.destroy()

    def save_game_record(self, winner):
        """Guarda el registro de la partida en la historia del juego."""
        record = {
            "Puntos Blanco": self.white_points.get(),
            "Puntos Negro": self.black_points.get(),
            "Ganador": winner,
            "Modo_Juego":self.game_mode.get(),
            "Level_White":self.selected_level.get(),
            "Level_Black":self.selected_level_ia.get()
        }
        self.game_history.append(record)
        with open("game_history.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Puntos Blanco", "Puntos Negro", "Ganador","Modo_Juego","Level_White","Level_Black"])
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(record)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHorsesGame(root)
    root.mainloop()