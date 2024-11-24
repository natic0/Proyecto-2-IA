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
        self.points_positions = {}
        self.x2_positions = set()
        self.white_horse = None
        self.black_horse = None
        self.white_points = tk.IntVar(value=0)
        self.black_points = tk.IntVar(value=0)
        self.turn = tk.StringVar(value="Turno: Caballo Blanco")
        self.white_x2 = False
        self.black_x2 = False

        # Archivo para guardar datos
        self.csv_file = "registro_jugadasv5.csv"
        self.init_csv()

        # Frames
        self.setup_ui()

    def init_csv(self):
        """Inicializa el archivo CSV y escribe los encabezados si está vacío."""
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "FilaCBA", "ColCBA", "FilaCNA", "ColCNA",
                "Valor(FilaCNA-1,ColCNA+2)",
                "Valor(FilaCNA-1,ColCNA-2)",
                "Valor(FilaCNA+1,ColCNA+2)",
                "Valor(FilaCNA+1,ColCNA-2)",
                "Valor(FilaCNA-2,ColCNA+1)",
                "Valor(FilaCNA-2,ColCNA-1)",
                "Valor(FilaCNA+2,ColCNA+1)",
                "Valor(FilaCNA+2,ColCNA-1)",
                "FilaCNE", "ColCNE", "Valor(FilaCNE,ColCNE)",
                "Puntaje Acumulado CN"
            ])

    def setup_ui(self):
        # Frame para selección de nivel
        level_frame = ttk.LabelFrame(self.root, text="Configuración del Juego")
        level_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(level_frame, text="Selecciona el nivel de dificultad:").grid(row=0, column=0, padx=5, pady=5)
        level_menu = ttk.OptionMenu(level_frame, self.selected_level, *self.levels)
        level_menu.grid(row=0, column=1, padx=5, pady=5)

        # Botón para iniciar el juego
        start_button = ttk.Button(level_frame, text="Iniciar Juego", command=self.start_game)
        start_button.grid(row=1, column=0, columnspan=2, pady=10)

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
                    command=lambda x=i, y=j: self.move_black_horse(x, y)
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
    def start_game(self):
        self.initialize_positions()
        self.update_board()
        self.enable_board()
        self.root.after(500, self.move_white_horse)
    def initialize_positions(self):
        # Reset tablero
        for row in self.board_buttons:
            for button in row:
                button.config(text="", state=tk.DISABLED, bg="SystemButtonFace")

        # Generar posiciones aleatorias
        positions = random.sample(range(64), 16)
        self.points_positions = {pos: i + 1 for i, pos in enumerate(positions[:10])}
        self.x2_positions = set(positions[10:14])
        self.white_horse = positions[14]
        self.black_horse = positions[15]

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
        self.board_buttons[bx][by].config(text="♘", bg="black", fg="white", state=tk.NORMAL)

    def enable_board(self):
        """Habilitar las casillas para el movimiento del caballo negro."""
        for row in self.board_buttons:
            for button in row:
                button.config(state=tk.NORMAL)
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
            self.root.after(500, self.move_white_horse)
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
            points = self.points_positions.get(move, 0)
            multiplier = 2 if move in self.x2_positions else 1
            move_score = self.minimax(move, depth - 1, False, float('-inf'), float('inf')) + points * multiplier
            if move_score > best_score:
                best_score = move_score
                best_move = move

        if best_move is not None:
            self.collect_points(best_move, "white")
            self.white_horse = best_move

        self.turn.set("Turno: Caballo Negro")
        self.update_board()
        self.check_game_end()


    def get_valid_moves(self, pos):
        """Devuelve una lista de movimientos válidos en 'L' para una posición."""
        x, y = divmod(pos, 8)
        moves = [
            (x + 2, y + 1), (x + 2, y - 1), (x - 2, y + 1), (x - 2, y - 1),
            (x + 1, y + 2), (x + 1, y - 2), (x - 1, y + 2), (x - 1, y - 2)
        ]
        moves = [
            x * 8 + y
            for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
            if 0 <= (nx := x + dx) < 8 and 0 <= (ny := y + dy) < 8
        ]
        return moves
       # return [nx * 8 + ny for nx, ny in moves if 0 <= nx < 8 and 0 <= ny < 8]

    def is_valid_move(self, current_pos, new_pos):
        """Verifica si un movimiento es válido en 'L'."""
        return new_pos in self.get_valid_moves(current_pos)        
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

    def check_game_end(self):
        """Verifica si el juego ha terminado."""
        if not self.points_positions:
            winner = "Empate"
            if self.white_points.get() > self.black_points.get():
                winner = "Caballo Blanco"
            elif self.black_points.get() > self.white_points.get():
                winner = "Caballo Negro"
            messagebox.showinfo("Juego Terminado", f"¡El juego ha terminado! Ganador: {winner}")
            self.root.destroy()

    def get_cell_value(self, x, y):
        """Devuelve el valor de una celda según su estado."""
        if not (0 <= x < 8 and 0 <= y < 8):
            return -1
        pos = x * 8 + y
        if pos == self.white_horse:
            return -1
        if pos in self.points_positions:
            return self.points_positions[pos]
        if pos in self.x2_positions:
            return 11
        return 0

    def log_move(self, cba_x, cba_y, cna_x, cna_y, cne_x, cne_y, cne_value, score):
        """Registra un movimiento en el archivo CSV."""
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Obtener valores de las casillas posibles en forma de "L"
            moves = [
                (cna_x - 1, cna_y + 2), (cna_x - 1, cna_y - 2),
                (cna_x + 1, cna_y + 2), (cna_x + 1, cna_y - 2),
                (cna_x - 2, cna_y + 1), (cna_x - 2, cna_y - 1),
                (cna_x + 2, cna_y + 1), (cna_x + 2, cna_y - 1)
            ]
            move_data = []
            for x, y in moves:
                move_data.extend([self.get_cell_value(x, y)])

            writer.writerow([
                cba_x, cba_y, cna_x, cna_y,
                *move_data, cne_x, cne_y, cne_value, score
            ])

    def move_black_horse(self, x, y):
        """Mueve el caballo negro a la posición seleccionada."""
        if self.turn.get() != "Turno: Caballo Negro":
            return

        pos = x * 8 + y
        if self.is_valid_move(self.black_horse, pos):
            # Registrar el movimiento
            cba_x, cba_y = divmod(self.white_horse, 8)
            cna_x, cna_y = divmod(self.black_horse, 8)
            cne_value = self.get_cell_value(x, y)
            self.log_move(cba_x, cba_y, cna_x, cna_y, x, y, cne_value, self.black_points.get())

            self.collect_points(pos, "black")
            self.black_horse = pos
            self.turn.set("Turno: Caballo Blanco")
            self.update_board()
            self.check_game_end()
            self.root.after(500, self.move_white_horse)
    def minimax(self, pos, depth, maximizing_player, alpha, beta):
        """Implementa el algoritmo Minimax con poda alfa-beta."""
        if depth == 0 or not self.points_positions:  # Condición de finalización
            return self.evaluate_board(pos, maximizing_player)

        valid_moves = self.get_valid_moves(pos)  # Obtiene movimientos válidos
        if maximizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
            # Copiar el estado actual del tablero para esta rama
                temp_positions = self.points_positions.copy()
                temp_x2 = self.x2_positions.copy()

            # Evaluar puntos
                points = temp_positions.pop(move, 0)
                multiplier = 2 if move in temp_x2 else 1
                eval_score = points * multiplier

            # Recursión en Minimax
                eval = self.minimax(move, depth - 1, False, alpha, beta) + eval_score
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval)

                if beta <= alpha:  # Poda alfa-beta
                    break

            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
            # Copiar el estado actual del tablero para esta rama
                temp_positions = self.points_positions.copy()
                temp_x2 = self.x2_positions.copy()

            # Evaluar puntos
                points = temp_positions.pop(move, 0)
                multiplier = 2 if move in temp_x2 else 1
                eval_score = points * multiplier

            # Recursión en Minimax
                eval = self.minimax(move, depth - 1, True, alpha, beta) - eval_score
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)

                if beta <= alpha:  # Poda alfa-beta
                    break

            return min_eval

    def evaluate_board(self, pos, maximizing_player):
        """Evalúa el estado del tablero."""
        points = self.points_positions.get(pos, 0)
        multiplier = 2 if pos in self.x2_positions else 1
        future_moves = len(self.get_valid_moves(pos))

    # Heurística: Prioriza puntos altos y movimientos futuros
        return points * multiplier + future_moves * 0.5



# Rest of the code remains unchanged.
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHorsesGame(root)
    root.mainloop()
