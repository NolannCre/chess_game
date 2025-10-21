from model import Game
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os


class ChessGUI:
    def __init__(self, root, game):
        self.root = root
        self.root.title("Jeu d'échecs")
        self.game = game
        self.image_folder = os.path.join(os.path.dirname(__file__), 'images')
        self.selected_square = None
        self.coup = 1
        
        # Pré-chargement des images
        self.images = {}
        self.load_images()
        
        # Création des éléments GUI
        self.couleur1 = "#F0D9B5" #clair
        self.couleur2 = "#B58863" #foncé
        self.create_menu()
        self.init_board()
        #self.menu_right()
        #self.create_move_history()
        
        # Affichage initial
        self.update_board()


    def load_images(self):
        pieces = ["pawn", "rook", "knight", "bishop", "queen", "king", 'checkmat']
        sizes = (60, 60)
        for i in [0, 1]:
            for color in ['white', 'black']:
                for piece in pieces:
                    a = "" if i==0 or piece=="king" or piece=="checkmat" else "2"
                    key = f"{piece}_{color}{a}"
                    path = os.path.join(self.image_folder, f"{key}.png")
                    if os.path.isfile(path):
                        img = Image.open(path).resize(sizes, Image.LANCZOS)
                        self.images[key] = ImageTk.PhotoImage(img)
                    else:
                        print(f"Image non trouvée : {path}")
           
            a = "" if i==0 else "2"
            key = f'case{a}'
            path = os.path.join(self.image_folder, f'{key}.png')
            if os.path.isfile(path):
                img = Image.open(path).resize(sizes, Image.LANCZOS)
                self.images[key] = ImageTk.PhotoImage(img)
            else:
                print(f"Image non trouvée : {key}")
           

    def theme_marron(self):
        self.couleur1 = "#F0D9B5" 
        self.couleur2 = "#B58863"
        self.theme()


    def theme_bleu(self):
        self.couleur1 = "#ccd2d8"
        self.couleur2 = "#005ec2"
        self.theme()


    def theme_vert(self):
        self.couleur1 = "#f9ffd2"
        self.couleur2 = "#68d669"
        self.theme()


    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="Nouvelle partie", command=self.new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Quitter", command=self.root.quit)
        menu_bar.add_cascade(label="Jeu", underline=0, menu=game_menu)


        game_menu2 = tk.Menu(menu_bar, tearoff=0)
        menu_recent = tk.Menu(menu_bar, tearoff=0)
        menu_recent.add_command(label="marron", command=self.theme_marron)
        menu_recent.add_command(label="bleu", command=self.theme_bleu)
        menu_recent.add_command(label="vert", command=self.theme_vert)
        game_menu2.add_cascade(label="thème", underline=0, menu=menu_recent)

        game_menu2.add_separator()
        game_menu2.add_command(label="truc", command=self.root.quit)
        menu_bar.add_cascade(label="Graphisme", underline=0, menu=game_menu2)
        self.root.config(menu=menu_bar)

    def theme(self):
        self.init_board()
        self.update_board()

    def init_board(self):
        # Création des boutons pour l'échiquier
        self.buttons = []
        for r in range(8):
            row_btns = []
            for c in range(8):
                if c in range(8):
                    color = self.couleur1 if (r + c) % 2 == 0 else self.couleur2
                else:
                    color = self.couleur1
                btn = tk.Button(self.root, bg=color, bd=0,
                                command=lambda r=r, c=c: self.on_click(r, c))
                btn.grid(row=r, column=c, sticky='nsew')
                row_btns.append(btn)
            self.buttons.append(row_btns)
        #redimensionnement uniforme
        for i in range(8):
            self.root.grid_rowconfigure(i, weight=1)
            self.root.grid_columnconfigure(i, weight=1)

            

            
    def menu_right(self):
        for r in range(8):
            for c in range(4):
                self.buttons[r][(c+8)].config(image=self.images["case"], 
                                                width=60, height=60) # Image sur le bouton        

    
    def create_move_history(self):
        # Listbox pour l'historique des coups
        self.history = tk.Listbox(self.root, height=6)
        self.history.grid(row=8, column=0, columnspan=8, sticky='nsew')
        self.root.grid_rowconfigure(8, weight=0)


    def update_board(self, r=range(8), c=range(8), target="" ,dest='true'):
        for row in r:
            for col in c:
                images = f'{self.game.get_piece(row, col)}{target}'
                if images:
                    if images in self.images:
                        if dest=='true':
                            # Conserve une référence à l'image dans l'attribut de la case
                            self.buttons[row][col].image = self.images[images]  
                            self.buttons[row][col].config(image=self.images[images], 
                                                        width=60, height=60) # Image sur le bouton
                        else:
                            if (row, col) in dest:
                                # Conserve une référence à l'image dans l'attribut de la case
                                self.buttons[row][col].image = self.images[images]  
                                self.buttons[row][col].config(image=self.images[images], 
                                                            width=60, height=60) # Image sur le bouton
                    else:
                        if not ('king' in images):
                            print(f"Erreur : {images} non trouvé dans images")  # Indique une erreur de clé


    def show_checkmat(self, winner):
        r, c = self.game.king_position[winner=='black']
        winner = "white" if winner == 'black' else 'black'
        images = f'checkmat_{winner}'
        self.buttons[r][c].image = self.images[images]  
        self.buttons[r][c].config(image=self.images[images], 
                                                        width=60, height=60)


    def on_click(self, row, col):
        # Gestion de la sélection et du déplacement
        if (row in range(8) and col in range(8)):
            if self.selected_square is None:
                if self.game.get_piece(row, col):
                    self.selected_square = (row, col)
                    r, c = [], []
                    dests = self.game._generate_legal_destinations(row, col)
                    for i in dests:
                        r2, c2 = i
                        r.append(r2)
                        c.append(c2)
                    self.update_board(r, c, target="2", dest=dests)
                else:
                    print("selectioner une piece")
                    #messagebox.showinfo("Information", "Sélectionner une pièce.")
            else:
                x1, y1 = self.selected_square
                print('vtf', x1, y1, row, col, self.game.is_valid_move(x1, y1, row, col, speak=True, update=True))
                if self.game.is_valid_move(x1, y1, row, col, speak=True, update=True):
                    print('???')
                    winner = self.game.current_turn
                    self.game.move_piece(x1, y1, row, col)
                    #move_notation = f"{self.game.current_turn}: ({x1},{y1})->({row},{col})"
                    #self.history.insert(tk.END, move_notation)
                    self.update_board()
                    print('go')
                    if self.game.is_checkmat(winner):
                        print("checkmate", winner)
                        self.show_checkmat(winner)
                        #messagebox.showinfo("Échec et mat", f"Partie terminée. {winner} a gagné !")
                    print("go-end")
                    if self.game.is_draw():
                        print("draw")
                    print('coup numéros:', self.coup)
                    self.coup += 1
                    #if self.game.is_king_in_check(self.game.piece):
                        #messagebox.showinfo('info', 'Echec')
                    
                    
                else:
                    self.update_board()
                    print("Mouvement illégal", self.game.piece)
                    #messagebox.showwarning("Mouvement illégal", "Ce déplacement n'est pas autorisé.")
                self.selected_square = None


    def new_game(self):
        # Réinitialiser la partie
        self.game = Game()
        #self.history.delete(0, tk.END)
        self.update_board()


def run_gui():
    root = tk.Tk()
    game = Game()
    gui = ChessGUI(root, game)
    root.mainloop()


if __name__ == '__main__':
    run_gui()

