from model import Game
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import os


class ChessGUI:
    def __init__(self, root, game):
        self.root = root
        self.root.title("♔ Jeu d'échecs ♔")
        self.root.configure(bg="#2C3E50")
        
        self.game = game
        self.image_folder = os.path.join(os.path.dirname(__file__), 'images')
        self.selected_square = None
        self.coup = 1
        
        self.bg_color = "#2C3E50"
        self.panel_color = "#34495E"
        self.accent_color = "#E74C3C"
        self.text_color = "#ECF0F1"
        self.text_color2 = "#E3E3E3" 
        self.button_color = "#3498DB"
        
        self.images = {}
        self.load_images()
        
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.side_container = tk.Frame(self.main_frame, bg=self.bg_color, relief="flat", bd=0)
        self.side_container.grid(row=0, column=1, sticky="nsew")       

        self.board_container = tk.Frame(self.main_frame, bg=self.panel_color, relief="raised", bd=3)
        self.board_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        self.board_frame = tk.Frame(self.board_container, bg="#8B4513", relief="raised", bd=5, padx=10, pady=10)
        self.board_frame.pack(fill=tk.BOTH, expand=True)
        
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        self.couleur1 = "#F0D9B5" 
        self.couleur2 = "#B58863" 
        self.move_history = False
        self.init_board()
        self.menu_manager = MenuManager(self)
        self.menu_manager.show_burger_closed()
        self.update_board()
        self.create_status_bar()
        

    def create_status_bar(self):
        """Crée une barre de statut en bas de la fenêtre"""
        self.status_frame = tk.Frame(self.root, bg=self.bg_color, height=30)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=20, pady=(0, 10))
        
        self.status_label = tk.Label(self.status_frame, 
                                    text="🎯 Sélectionnez une pièce pour commencer", 
                                    font=("Segoe UI", 10), 
                                    fg=self.text_color, bg=self.bg_color)
        self.status_label.pack(side=tk.LEFT)
        
        self.player_indicator = tk.Label(self.status_frame, 
                                        text="⚫ Blancs", 
                                        font=("Segoe UI", 10, "bold"), 
                                        fg="#FFD700", bg=self.bg_color)
        self.player_indicator.pack(side=tk.RIGHT)


    def load_images(self):
        pieces = ["pawn", "rook", "knight", "bishop", "queen", "king", 'checkmat']
        sizes = (50, 50)
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
            
            for key in ['case', 'case2', 'menu_burger']:
                path = os.path.join(self.image_folder, f'{key}.png')
                if os.path.isfile(path):
                    img = Image.open(path).resize(sizes, Image.LANCZOS)
                    self.images[key] = ImageTk.PhotoImage(img)
                else:
                    print(f"Image non trouvée : {key}")


    def delete_frame(self, frame):
        for widget in frame.winfo_children():
            widget.pack_forget()
 

    def change_menu(self, frame, frame_to):
        frame.destroy()
        frame_to()


    def theme_marron(self):
        self.couleur1 = "#F0D9B5" 
        self.couleur2 = "#B58863"
        self.board_frame.configure(bg="#8B4513")
        self.theme()


    def theme_bleu(self):
        self.couleur1 = "#DEE3E8"
        self.couleur2 = "#4A90E2"
        self.board_frame.configure(bg="#2C5282")
        self.theme()


    def theme_vert(self):
        self.couleur1 = "#F0F8E8"
        self.couleur2 = "#7CB342"
        self.board_frame.configure(bg="#4A7C59")
        self.theme()


    def theme(self):
        self.init_board()
        self.update_board()


    def init_board(self):
        self.buttons = []
        for r in range(8):
            row_btns = []
            for c in range(8):
                color = self.couleur1 if (r + c) % 2 == 0 else self.couleur2
                btn = tk.Button(self.board_frame, bg=color, bd=2, relief="flat",
                                activebackground="#FFD700", cursor="hand2",
                                command=lambda r=r, c=c: self.on_click(r, c))
                btn.grid(row=r, column=c, sticky='nsew', padx=1, pady=1)
                row_btns.append(btn)
            self.buttons.append(row_btns)
        
        for i in range(8):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)


    def move_container(self, configur=None, relief='flat'):
        self.moves_container = tk.Frame(self.side_container, bg=self.bg_color, relief=relief, bd=3)
        self.moves_container.grid(row=0, column=1, sticky="nsew")
        if configur != None: self.moves_container.configure(width=configur)

    
    def button_option(self, root, text='', command=None):
        option = tk.Button(root, bg=self.panel_color,
                            text=text, fg=self.text_color,
                            bd=0, relief="flat",
                             font=("Segoe UI", 10, "bold"),
                            activebackground=self.bg_color, cursor="hand2",
                            command=lambda: command())
        option.pack(fill=tk.X, expand=False, padx=5, pady=2)


    def menu_burger(self):   
        self.move_container(configur=20)

        burger = tk.Button(self.moves_container, bg=self.bg_color,
                            bd=0, relief="flat",
                            activebackground=self.bg_color, cursor="hand2",
                            command=lambda: self.change_menu(self.moves_container, self.menu_burger_open))
        burger.pack(fill=tk.X, expand=False, padx=10, pady=2)
        burger.config(image=self.images['menu_burger'], width=30, height=30)


    def menu_burger_open(self):
        self.move_container(configur=350, relief='raise')
    
        self.moves_frame = tk.Frame(self.moves_container, bg=self.panel_color)
        self.moves_frame.pack(fill=tk.BOTH, expand=True)

        options_title_frame = tk.Frame(self.moves_frame, bg=self.bg_color)
        options_title_frame.pack(fill=tk.X, pady=(0, 5))
    
        options_title_label = tk.Label(options_title_frame, text="Options",
                            font=("Segoe UI", 14, "bold"),
                            fg=self.text_color2, bg=self.bg_color)
        options_title_label.pack(side="right",expand=True, padx=0, pady=0)

        retour = tk.Button(options_title_frame, bg=self.bg_color,
                            text='❌', fg=self.text_color,
                            bd=0, relief="flat",
                             font=("Segoe UI", 10, "bold"),
                            activebackground=self.bg_color, cursor="hand2",
                            command=lambda: self.change_menu(self.moves_container, self.menu_burger))
        retour.pack(side="left", expand=False, padx=0, pady=0)
        
        self.button_option(self.moves_frame, text='Historique des coups', command=self.create_move_history)
        self.button_option(self.moves_frame, text='Nouvelle partie', command=self.new_game)
        self.button_option(self.moves_frame, text='Quitter', command=self.root.quit)

        settings_title_frame = tk.Frame(self.moves_frame, bg=self.bg_color)
        settings_title_frame.pack(fill=tk.X, pady=(0, 5))
        
        settings_title_label = tk.Label(settings_title_frame, text="Paramètres",
                                font=("Segoe UI", 14, "bold"),
                                fg=self.text_color2, bg=self.bg_color)
        settings_title_label.pack(fill=tk.X, padx=100, pady=0)

        self.button_option(self.moves_frame, text='Thèmes', command=self.menu_burger_open)


    def create_move_history(self):
        """Crée l'interface pour l'historique des coups avec style moderne"""
        self.move_container(configur=350, relief='raise')

        self.moves_frame = tk.Frame(self.moves_container, bg=self.panel_color)
        self.moves_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        title_frame = tk.Frame(self.moves_frame, bg=self.panel_color)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(title_frame, text="📋 HISTORIQUE DES COUPS", 
                              font=("Segoe UI", 14, "bold"), 
                              fg=self.text_color, bg=self.panel_color)
        title_label.pack()
        
        self.info_frame = tk.Frame(self.moves_frame, bg=self.panel_color)
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.turn_label = tk.Label(self.info_frame, text="🔵 Tour: Blancs", 
                                  font=("Segoe UI", 10, "bold"), 
                                  fg=self.text_color, bg=self.panel_color)
        self.turn_label.pack(side=tk.LEFT)
        
        self.move_count_label = tk.Label(self.info_frame, text="Coup: 1", 
                                        font=("Segoe UI", 10), 
                                        fg=self.text_color, bg=self.panel_color)
        self.move_count_label.pack(side=tk.RIGHT)
        

        text_frame = tk.Frame(self.moves_frame, bg=self.panel_color, relief="sunken", bd=2)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.moves_text = scrolledtext.ScrolledText(text_frame, width=25, height=18, 
                                                   state=tk.DISABLED, wrap=tk.WORD,
                                                   bg="#1E2833", fg=self.text_color,
                                                   font=("Consolas", 10),
                                                   selectbackground=self.accent_color,
                                                   insertbackground=self.text_color,
                                                   relief="flat", bd=0)
        self.moves_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = tk.Frame(self.moves_frame, bg=self.panel_color)
        button_frame.pack(fill=tk.X)
        
        button_style = {
            "font": ("Segoe UI", 9, "bold"),
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "activebackground": "#2980B9"
        }
        
        clear_btn = tk.Button(button_frame, text="🗑️ Effacer", 
                             command=self.clear_history,
                             bg=self.accent_color, fg="white",
                             **button_style)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10), pady=5, fill=tk.X, expand=True)
        
        save_btn = tk.Button(button_frame, text="💾 Sauvegarder", 
                            command=self.save_game,
                            bg=self.button_color, fg="white",
                            **button_style)
        save_btn.pack(side=tk.LEFT, padx=(10, 0), pady=5, fill=tk.X, expand=True)


    def add_move_to_history(self, move_from, move_to, piece_moved, captured=None):
        """Ajoute un coup à l'historique avec style amélioré"""
        self.moves_text.config(state=tk.NORMAL)
        
        cols = "abcdefgh"
        from_notation = f"{cols[move_from[1]]}{8-move_from[0]}"
        to_notation = f"{cols[move_to[1]]}{8-move_to[0]}"
        
        piece_symbols = {
            'pawn': '', 'rook': '♜', 'knight': '♞', 
            'bishop': '♝', 'queen': '♛', 'king': '♚'
        }
        
        piece_type = piece_moved.split('_')[0] if piece_moved else ''
        piece_symbol = piece_symbols.get(piece_type, '')
        
        capture_symbol = " ⚔️ " if captured else " → "
        move_notation = f"{piece_symbol}{from_notation}{capture_symbol}{to_notation}"
        
        if self.game.current_turn == 'black': 
            self.moves_text.insert(tk.END, f"⚫ {self.coup}. {move_notation}    ")
            self.update_turn_display("⚪ Noirs")
        else:
            self.moves_text.insert(tk.END, f"⚪ {move_notation}\n")
            self.coup += 1
            self.update_turn_display("⚫ Blancs")
        
        self.move_count_label.config(text=f"Coup: {self.coup}")
        
        self.moves_text.config(state=tk.DISABLED)
        self.moves_text.see(tk.END) 

    def update_turn_display(self, turn_text):
        """Met à jour l'affichage du tour"""
        self.turn_label.config(text=f"🎯 Tour: {turn_text}")
        if "Blancs" in turn_text:
            self.player_indicator.config(text="⚫ Blancs", fg="#FFD700")
        else:
            self.player_indicator.config(text="⚪ Noirs", fg="#C0C0C0")

    def clear_history(self):
        """Efface l'historique des coups"""
        self.moves_text.config(state=tk.NORMAL)
        self.moves_text.delete(1.0, tk.END)
        self.moves_text.config(state=tk.DISABLED)
        self.coup = 1
        self.move_count_label.config(text="Coup: 1")
        self.update_turn_display("⚪ Blancs")
        self.status_label.config(text="🎯 Sélectionnez une pièce pour commencer")

    def save_game(self):
        """Sauvegarde la partie"""
        try:
            historique = self.moves_text.get(1.0, tk.END)
            with open("partie_echecs.txt", "w") as f:
                f.write(f"Partie d'échecs\n")
                f.write(f"================\n\n")
                f.write(historique)
            messagebox.showinfo("Sauvegarde", "Partie sauvegardée dans 'partie_echecs.txt'")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")


    def menu_theme(self):
        self.move_container(configur=350, relief='raise')
    
        self.moves_frame = tk.Frame(self.moves_container, bg=self.panel_color)
        self.moves_frame.pack(fill=tk.BOTH, expand=True)

        options_title_frame = tk.Frame(self.moves_frame, bg=self.bg_color)
        options_title_frame.pack(fill=tk.X, pady=(0, 5))
    
        options_title_label = tk.Label(options_title_frame, text="Thèmes",
                            font=("Segoe UI", 14, "bold"),
                            fg=self.text_color2, bg=self.bg_color)
        options_title_label.pack(side="right",expand=True, padx=0, pady=0)

        retour = tk.Button(options_title_frame, bg=self.bg_color,
                            text='❌', fg=self.text_color,
                            bd=0, relief="flat",
                             font=("Segoe UI", 10, "bold"),
                            activebackground=self.bg_color, cursor="hand2",
                            command=lambda: self.change_menu(self.moves_container, self.menu_burger))
        retour.pack(side="left", expand=False, padx=0, pady=0)

        self.button_option(self.moves_frame, text='bleu', command=self.theme_bleu)
        self.button_option(self.moves_frame, text='vert', command=self.theme_vert)
        self.button_option(self.moves_frame, text='marron', command=self.theme_marron)

        

    def update_board(self, r=range(8), c=range(8), target="" ,dest='true'):
        for row in r:
            for col in c:
                images = f'{self.game.get_piece(row, col)}{target}'
                if images:
                    if images in self.images:
                        if dest=='true':
                            self.buttons[row][col].image = self.images[images]  
                            self.buttons[row][col].config(image=self.images[images])
                        else:
                            if (row, col) in dest:
                                self.buttons[row][col].image = self.images[images]  
                                self.buttons[row][col].config(image=self.images[images]) 
                    else:
                        if not ('king' in images):
                            print(f"Erreur : {images} non trouvé dans images") 

        for i in range(8):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)


    def show_checkmat(self, winner):
        r, c = self.game.king_position[winner=='black']
        winner = "white" if winner == 'black' else 'black'
        images = f'checkmat_{winner}'
        self.buttons[r][c].image = self.images[images]  
        self.buttons[r][c].config(image=self.images[images], 
                                                        width=60, height=60)


    def on_click(self, row, col):
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
                    
                    piece_name = self.game.get_piece(row, col).replace('_', ' ').title()
                    self.status_label.config(text=f"🎯 {piece_name} sélectionnée - Choisissez une destination")
                else:
                    self.status_label.config(text="❌ Sélectionnez une pièce valide")
            else:
                x1, y1 = self.selected_square
                if self.game.is_valid_move(x1, y1, row, col, speak=True, update=True):
                    winner = self.game.current_turn
                    
                    piece_moved = self.game.get_piece(x1, y1)
                    piece_captured = True if abs(self.game.board[row, col]) in (1,2, 3, 4, 5, 6) else False
                    
                    self.game.move_piece(x1, y1, row, col)
                
                    if self.move_history: self.add_move_to_history((x1, y1), (row, col), piece_moved, piece_captured)
                    
                    self.update_board()
                    
                    if self.game.is_checkmat(winner):
                        self.show_checkmat(winner)
                        self.status_label.config(text=f"🏆 ÉCHEC ET MAT ! {winner} ont gagné !")
                        self.moves_text.config(state=tk.NORMAL)
                        self.moves_text.insert(tk.END, " 🏆 # ")
                        self.moves_text.config(state=tk.DISABLED)
                    elif self.game.is_draw():
                        self.status_label.config(text="🤝 MATCH NUL - Partie terminée")
                        self.moves_text.config(state=tk.NORMAL)
                        self.moves_text.insert(tk.END, " 🤝 ")
                        self.moves_text.config(state=tk.DISABLED)
                    else:
                        current_player = "Blancs" if self.game.current_turn == "white" else "Noirs"
                        self.status_label.config(text=f"✅ Coup joué - Au tour des {current_player}")
                else:
                    self.update_board()
                    self.status_label.config(text="❌ Mouvement illégal - Essayez autre chose")
                self.selected_square = None

    def new_game(self):
        self.game = Game()
        if self.move_history: self.clear_history()
        self.update_board()
        self.status_label.config(text="🆕 Nouvelle partie commencée - Au tour des Blancs")

        self.update_board()



class MenuManager:
    """Gestionnaire pour tous les menus latéraux"""
    
    def __init__(self, parent_gui):
        self.gui = parent_gui
        self.current_menu = None
        

    def create_base_container(self, width=350, relief='flat'):
        """Crée le conteneur de base pour tous les menus"""
        if hasattr(self.gui, 'moves_container'):
            self.gui.moves_container.destroy()
            
        self.gui.moves_container = tk.Frame(
            self.gui.side_container, 
            bg=self.gui.bg_color, 
            relief=relief, 
            bd=3,
            width=width
        )
        self.gui.moves_container.grid(row=0, column=1, sticky="nsew")
        return self.gui.moves_container
    

    def create_header(self, container, title, show_back=True):
        """Crée un en-tête standardisé pour les menus"""
        header_frame = tk.Frame(container, bg=self.gui.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        if show_back:
            back_btn = tk.Button(
                header_frame, 
                text='❌', 
                bg=self.gui.bg_color,
                fg=self.gui.text_color,
                bd=0, 
                relief="flat",
                font=("Segoe UI", 10, "bold"),
                activebackground=self.gui.bg_color, 
                cursor="hand2",
                command=self.show_burger_closed
            )
            back_btn.pack(side="left", padx=5)
        
        title_label = tk.Label(
            header_frame, 
            text=title,
            font=("Segoe UI", 14, "bold"),
            fg=self.gui.text_color2, 
            bg=self.gui.bg_color
        )
        title_label.pack(side="right", expand=True, padx=10)
        
        return header_frame
    

    def create_menu_button(self, parent, text, command, style_override=None):
        """Crée un bouton de menu standardisé"""
        style = {
            "bg": self.gui.panel_color,
            "fg": self.gui.text_color,
            "bd": 0,
            "relief": "flat",
            "font": ("Segoe UI", 10, "bold"),
            "activebackground": self.gui.bg_color,
            "cursor": "hand2"
        }
        
        if style_override:
            style.update(style_override)
            
        btn = tk.Button(parent, text=text, command=command, **style)
        btn.pack(fill=tk.X, expand=False, padx=5, pady=2)
        return btn
    

    def show_burger_closed(self):
        """Affiche le menu burger fermé (juste l'icône)"""
        self.current_menu = "closed"
        container = self.create_base_container(width=60, relief='flat')
        
        burger_btn = tk.Button(
            container,
            bg=self.gui.bg_color,
            bd=0,
            relief="flat",
            activebackground=self.gui.bg_color,
            cursor="hand2",
            command=self.show_main_menu
        )
        burger_btn.pack(fill=tk.X, expand=False, padx=10, pady=2)
        
        if 'menu_burger' in self.gui.images:
            burger_btn.config(
                image=self.gui.images['menu_burger'], 
                width=30, 
                height=30
            )
    
    
    def show_main_menu(self):
        """Affiche le menu principal avec toutes les options"""
        self.current_menu = "main"
        container = self.create_base_container(relief='raised')
        
        # Frame principal
        main_frame = tk.Frame(container, bg=self.gui.panel_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # En-tête
        self.create_header(main_frame, "Options")
        
        # Section Actions
        self.create_menu_button(main_frame, " Historique des coups", self.show_move_history)
        self.create_menu_button(main_frame, " Nouvelle partie", self.gui.new_game)
        self.create_menu_button(main_frame, " Quitter", self.gui.root.quit)
        
        # Séparateur
        separator = tk.Frame(main_frame, bg=self.gui.bg_color, height=2)
        separator.pack(fill=tk.X, pady=10)
        
        # Section Paramètres
        settings_header = tk.Label(
            main_frame, 
            text="Paramètres",
            font=("Segoe UI", 14, "bold"),
            fg=self.gui.text_color2, 
            bg=self.gui.panel_color
        )
        settings_header.pack(pady=5)
        
        self.create_menu_button(main_frame, " Thèmes", self.show_theme_menu)
    

    def show_move_history(self):
        """Affiche le menu d'historique des coups"""
        self.current_menu = "history"
        self.gui.move_history = True
        container = self.create_base_container(relief='raised')
        
        # Frame principal
        main_frame = tk.Frame(container, bg=self.gui.panel_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # En-tête
        self.create_header(main_frame, " HISTORIQUE DES COUPS")
        
        # Frame d'informations
        info_frame = tk.Frame(main_frame, bg=self.gui.panel_color)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.gui.turn_label = tk.Label(
            info_frame, 
            text="🔵 Tour: Blancs",
            font=("Segoe UI", 10, "bold"),
            fg=self.gui.text_color, 
            bg=self.gui.panel_color
        )
        self.gui.turn_label.pack(side=tk.LEFT)
        
        self.gui.move_count_label = tk.Label(
            info_frame, 
            text="Coup: 1",
            font=("Segoe UI", 10),
            fg=self.gui.text_color, 
            bg=self.gui.panel_color
        )
        self.gui.move_count_label.pack(side=tk.RIGHT)
        
        # Zone de texte pour l'historique
        text_frame = tk.Frame(main_frame, bg=self.gui.panel_color, relief="sunken", bd=2)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.gui.moves_text = scrolledtext.ScrolledText(
            text_frame, 
            width=25, 
            height=18,
            state=tk.DISABLED, 
            wrap=tk.WORD,
            bg="#1E2833", 
            fg=self.gui.text_color,
            font=("Consolas", 10),
            selectbackground=self.gui.accent_color,
            insertbackground=self.gui.text_color,
            relief="flat", 
            bd=0
        )
        self.gui.moves_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Boutons d'action
        self._create_history_buttons(main_frame)
    

    def _create_history_buttons(self, parent):
        """Crée les boutons pour l'historique"""
        button_frame = tk.Frame(parent, bg=self.gui.panel_color)
        button_frame.pack(fill=tk.X)
        
        button_style = {
            "font": ("Segoe UI", 9, "bold"),
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "activebackground": "#2980B9"
        }
        
        clear_btn = tk.Button(
            button_frame, 
            text=" Effacer",
            command=self.gui.clear_history,
            bg=self.gui.accent_color, 
            fg="white",
            **button_style
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10), pady=5, fill=tk.X, expand=True)
        
        save_btn = tk.Button(
            button_frame, 
            text=" Sauvegarder",
            command=self.gui.save_game,
            bg=self.gui.button_color, 
            fg="white",
            **button_style
        )
        save_btn.pack(side=tk.LEFT, padx=(10, 0), pady=5, fill=tk.X, expand=True)
    

    def show_theme_menu(self):
        """Affiche le menu de sélection des thèmes"""
        self.current_menu = "themes"
        container = self.create_base_container(relief='raised')
        
        # Frame principal
        main_frame = tk.Frame(container, bg=self.gui.panel_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # En-tête
        self.create_header(main_frame, "Thèmes")
        
        # Boutons de thèmes avec prévisualisation
        themes = [
            (" Thème Marron", self.gui.theme_marron, "#8B4513"),
            (" Thème Bleu", self.gui.theme_bleu, "#2C5282"),
            (" Thème Vert", self.gui.theme_vert, "#4A7C59")
        ]
        
        for name, command, color in themes:
            btn_frame = tk.Frame(main_frame, bg=self.gui.panel_color)
            btn_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Aperçu de couleur
            color_preview = tk.Frame(btn_frame, bg=color, width=20, height=20)
            color_preview.pack(side=tk.LEFT, padx=(0, 10), pady=5)
            
            # Bouton de thème
            theme_btn = tk.Button(
                btn_frame,
                text=name,
                command=lambda cmd=command: self._apply_theme_and_return(cmd),
                bg=self.gui.panel_color,
                fg=self.gui.text_color,
                bd=0,
                relief="flat",
                font=("Segoe UI", 10, "bold"),
                activebackground=self.gui.bg_color,
                cursor="hand2"
            )
            theme_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
    

    def _apply_theme_and_return(self, theme_command):
        """Applique un thème et retourne au menu principal"""
        theme_command()
        self.show_main_menu()



def run_gui():
    root = tk.Tk()
    game = Game()
    gui = ChessGUI(root, game)
    root.mainloop()


if __name__ == '__main__':
    run_gui()