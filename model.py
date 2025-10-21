import numpy as np
from tkinter import messagebox


class Game:
    def __init__(self):
        self.board = self.init_board()
        self.current_turn = 'white'  
        self.king_position = {True: (7, 4), False: (0, 4)} #blanc: (True); noir: (False)
        self.king_moved = {True: False, False: False}  
        self.rook_moved = {True: [False, False], False: [False, False]}
        self.en_passant = {"target": None, 'bool': False, 'bool2': False}
        self.check = None
    

    def init_board(self):
        # Initialiser l'échiquier avec numpy
        board = np.zeros((8, 8), dtype=int)
        board[1, :] = -1  
        board[6, :] = 1  
        order = [-2, -3, -4, -5, -6, -4, -3, -2]
        board[0, :] = order
        board[7, :] = [-x for x in order] 
        return board


    def get_piece(self, row, col):
            piece = self.board[row, col]
            piece_names = {
                1: "pawn_white", -1: "pawn_black",
                2: "rook_white", -2: "rook_black",
                3: "knight_white", -3: "knight_black",
                4: "bishop_white", -4: "bishop_black",
                5: "queen_white", -5: "queen_black",
                6: "king_white", -6: "king_black",
                0:'case'
            }
            return piece_names.get(piece)
    

    def play_turn(self, x1, y1, speak=False):
        piece = self.board[x1, y1]
        valid = True
        msg = None
        if piece == 0:
            msg = "Aucune pièce à déplacer !"
            valid = False
        elif ((self.current_turn == 'white') and (piece < 0)) or ((self.current_turn == 'black') and (0 < piece)):
            msg = "Ce n'est pas votre tour"
            valid = False
        if (speak) and (msg != None):
            print(msg)
        return valid


    def promotion(self, piece, x2, y2):
        if (piece == 1 and x2 == 0):
            self.board[x2, y2] = 5 
        if (piece == -1 and x2 == 7):
            self.board[x2, y2] = -5  
    
    
    def move_piece(self, x1, y1, x2, y2, update=True):
        piece = self.board[x1, y1]
        if abs(piece) != 6 and abs(piece) != 0:
            self.board[x1, y1] = 0  
            self.board[x2, y2] = piece 
        if abs(piece) == 6:
            if self.is_valid_castling(x1, y1, y2):
                self.perform_castling( piece, x1, y1, y2)
            else:
                self.old_board = self.board
                self.board[x1, y1] = 0  
                self.board[x2, y2] = piece  

        self.promotion(piece, x2, y2)
        
        # Mise a jour déplacement roi / tour / prise en passant
        if update:
            if abs(piece) == 6:
                self.king_moved[piece > 0] = True
                self.king_position[piece>0] = (x2, y2)
            elif abs(piece) == 2 and (y1 in (0,7)):
                self.rook_moved[piece > 0][0 if y1==0 else 1] = True
            if self.en_passant['bool']:
                self.board[x2-self.direction, y2] = 0 
            self.current_turn= "black" if self.current_turn == "white" else "white"

    
    def is_opponent_piece(self, x2, y2):
        target_piece = self.board[x2, y2]
        if target_piece == 0:
            return True
        return ((self.piece>0) == (target_piece<0))


    def is_valid_move(self, x1, y1, x2, y2, speak=False, update=False):
        # Vérifie que le coup est valide
        self.updtate = update
        self.piece = self.board[x1, y1]
        print("piece :", self.piece)
        print('turn :', self.current_turn)
        if not self.play_turn(x1, y1, speak):
            return False
        valid = True
        valid = {
        1: self.is_valid_pawn_move,
        2: self.is_valid_rook_move,
        3: self.is_valid_knight_move,
        4: self.is_valid_bishop_move,
        5: self.is_valid_queen_move,
        6: self.is_valid_king_move,
            }[abs(self.piece)](x1, y1, x2, y2)
        print('valid :', valid)
        if abs(self.piece) != 6:
            valid = valid and self.is_opponent_piece(x2, y2)
        if not valid:  
            return False
        # Simuler le coup et vérifier qu’on ne se met pas en échec
        backup = self.board.copy()
        self.move_piece(x1,y1,x2,y2, update=False)
        is_white = self.piece>0
        if abs(self.piece) != 6:
            r, c = self.king_position[is_white]
        else:
            r, c = x2, y2 
        in_check = self.is_square_attacked(r, c)
        print('valid1 :', not in_check, r,c, self.piece)
        self.board = backup
        if update and not in_check:
            if self.en_passant['bool2']:
                self.en_passant['target'] = None
                self.en_passant['bool2'] = False
            else:
                self.en_passant['bool2']= True
        self.updtate = False
        print('valid2 :', not in_check)
        return not in_check
            
   
    def is_valid_pawn_move(self, x1, y1, x2, y2):
            self.direction = -1 if self.piece > 0 else 1
            start_rank = 6 if self.piece > 0 else 1
            # Avance simple
            if x2 == x1 + self.direction and y2 == y1 and self.board[x2, y2] == 0:
                return True

            # Double avance initiale
            if x1 == start_rank and x2 == x1 + 2 * self.direction and y2 == y1:
                if self.board[x1 + self.direction, y1] == 0 and self.board[x2, y2] == 0:
                    self.en_passant['target'] = (x2, y2)
                    return True

            # Capture normale
            if x2 == x1 + self.direction and abs(y2 - y1) == 1:
                if self.board[x2, y2] != 0:
                    return True
            
            # En passant
            if (self.en_passant['target'] == (x1, y2)):
                    if self.updtate:
                        self.en_passant['bool'] = True
                    return True

            return False


    def is_valid_rook_move(self, x1, y1, x2, y2):
        if x1 != x2 and y1 != y2:
            return False # pas en ligne droite
        
        # Vérifier qu'il n'y a pas d'obstacles 
        if x1 == x2:  # Déplacement horizontal
            step = 1 if y2 > y1 else -1
            for y in range(y1 + step, y2, step):
                if self.board[x1, y] != 0:
                    return False
        else:  # Déplacement vertical
            step = 1 if x2 > x1 else -1
            for x in range(x1 + step, x2, step):
                if self.board[x, y1] != 0:
                    return False
                
        return True
    

    def is_valid_knight_move(self, x1, y1, x2, y2):
        return (abs(x2 - x1), abs(y2 - y1)) in [(2, 1), (1, 2)]
    

    def is_valid_bishop_move(self, x1, y1, x2, y2):
        if abs(x2 - x1) != abs(y2 - y1):
            return False  # pas en diagonale
        
        # Vérifier qu'il n'y a pas d'obstacles entre la position initiale et la position finale
        x_step = 1 if x2 > x1 else -1
        y_step = 1 if y2 > y1 else -1
        for i in range(1, abs(x2 - x1)):
            if self.board[x1 + i * x_step, y1 + i * y_step] != 0:
                return False
        
        return True


    def is_valid_queen_move(self, x1, y1, x2, y2):
        # Elle se déplacer comme une tour et un fou
        return self.is_valid_rook_move(x1, y1, x2, y2) or self.is_valid_bishop_move(x1, y1, x2, y2)


    def is_valid_king_move(self, x1, y1, x2, y2):
        if (max(abs(x2 - x1), abs(y2 - y1)) == 1) and (not self.is_square_attacked(x2, y2, is_white=(self.board[x1, y1]>0))) and self.is_opponent_piece(x2, y2): 
            return self.is_opponent_piece(x2, y2)
        return self.is_valid_castling(x1, y1, y2)

    
    def will_king_pass_through_check(self, piece, x2, y2):
        row, col = x2, y2
        is_white = piece>0
        return self.is_square_attacked(row, col, is_white) 


    def is_king_in_check(self, piece):
        # Détermine la position du roi blanc ou noir
        row, col = self.king_position[piece>0]
        is_white = piece>0
        return self.is_square_attacked(row, col, is_white)
        
    
    def is_valid_castling(self, x1, y1, y2):
        piece = self.board[x1][y1] 
        x2 = x1
        if y2 == y1 + 2:  # Petit roque (vers la droite)
            if self.king_moved[piece>0] or self.rook_moved[piece>0][1]:  # Si le roi ou la tour de droite a bougé
                print("king :", self.king_moved[piece>0])
                return False
            # Vérifier que le chemin est libre que le roi n'est pas en échec et qu'il ne vas pas sur une case attaquée
            return (not self.is_path_blocked(x1, y1, y2)) and (not self.is_king_in_check(piece)) and (not self.will_king_pass_through_check(piece, x2, y2))
        elif y2 == y1 - 2:  # Grand roque (vers la gauche)
            if self.king_moved[piece > 0] or self.rook_moved[piece > 0][0]:  # Si le roi ou la tour de gauche a bougé
                return False
            # Vérifier que le chemin est libre et que le roi ne passe pas par une case attaquée
            return not self.is_path_blocked(x1, y1, y2) and not self.is_king_in_check(piece) and not self.will_king_pass_through_check(piece, x2, y2)
        return False
    
    def is_path_blocked(self, x2, y1, y2):
        #vérifier que le chemin entre la tour et le roi est vide
        start, end = min(y1, y2), max(y1, y2)

        # Vérifier que toutes les cases  dans ]y1; y2[ sont vides
        for col in range(start + 1, end):
            if self.board[x2, col] != 0:
                return True  # Il y a une pièce qui bloque le chemin
        return False  # Le chemin est libre


    def perform_castling(self, piece, x1, y1, y2):
        if y2 == y1 + 2:  # Petit roque
            self.old_board = self.board 
            # Déplacement du roi
            self.board[x1, y1] = 0
            self.board[x1, y1 + 2] = piece
            # Déplacement de la tour
            self.board[x1, y1 + 3] = 0
            self.board[x1, y1 + 1] = 2 if piece > 0 else -2  # tour blanche ou noire
        elif y2 == y1 - 2:  # Grand roque
            self.old_board = self.board
            self.board[x1, y1] = 0
            self.board[x1, y1 - 2] = piece
            # Déplacement de la tour
            self.board[x1, y1 - 4] = 0
            self.board[x1, y1 - 1] = 2 if piece > 0 else -2  # tour blanche ou noire

    
    def is_square_attacked(self, row: int, col: int, is_white="") -> bool:
        """
        Vérifie si la case (row, col) est attaquée par au moins une pièce 
        de la couleur opposée a is_white.
        """
        board = self.board.copy()
        is_white = board[row, col] > 0 if is_white == "" else is_white
        print("sq", is_white, row, col)
        # --- 1. Attaque par pions ---
        pawn_dirs = [(-1,-1), (-1,1)] if is_white else [(1,-1), (1,1)]
        for dr, dc in pawn_dirs:
            r, c = row + dr, col + dc
            print(r, c, 'pawn', row, col)
            if (r in range(8)) and (c in range(8)):
                if board[r,c] == (-1 if is_white else 1):
                    self.check = (r, c)
                    print(1, "sq")
                    return True
                
         # --- 2. Attaque par cavaliers ---
        knight_offsets = [
            (2,1),(2,-1),(-2,1),(-2,-1),
            (1,2),(1,-2),(-1,2),(-1,-2),
        ]
        for dr, dc in knight_offsets:
            r, c = row+dr, col+dc
            if (r in range(8)) and (c in range(8)):
                if board[r,c] == (-3 if is_white else 3):
                    self.check = (r, c)
                    print(2, self.check, is_white, row, col)
                    return True

        # --- 3. Attaque par tour / dame (orthogonal) ---
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            r, c = row + dr, col + dc
            while (r in range(8)) and (c in range(8)):
                piece = board[r,c]
                if piece != 0:
                    # si c'est une tour ou une dame adverse
                    if (is_white and piece in (-2, -5)) or ((not is_white) and (piece in (2, 5))):
                        self.check = (r, c)
                        return True
                    break
                r += dr; c += dc

        # --- 4. Attaque par fou / dame (diagonales) ---
        for dx, dy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            nx, ny = row + dx, col + dy
            while (nx in range(8)) and (ny in range(8)): 
                piece = board[nx, ny]
                if piece != 0:
                    if (is_white and (piece in (-4, -5))) or ((not is_white) and (piece in (4, 5))):    
                        if (piece > 0) != is_white:
                            return True
                        break
                    break
                nx += dx; ny += dy

        # --- 5. Attaque par roi (adjacent) ---
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr==0 and dc==0: continue
                r, c = row + dr, col + dc
                if (r in range(8)) and (c in range(8)):
                    if board[r,c] == (-6 if is_white else 6):
                        self.check = (r, c)
                        print(5, self.check)
                        return True

        return False
    

    def is_checkmat(self, turn=""):
        is_white = self.piece > 0 if turn=="" else (True if turn=="white" else False)
        print(0)
        print(is_white, "is_white")
        print("")
        
        king_position = self.king_position[not is_white]

        if king_position is None:
            return False
        
        rowk, colk = self.king_position[not is_white]

        if not self.is_square_attacked(rowk, colk):
            return False  # Pas d’échec, donc pas d’échec et mat
        print(1, "echec")
        print('')
       # 2) Can the king move to any square so that it's not in check?
        for (r2, c2) in self._generate_legal_destinations(rowk, colk):
            if self.is_valid_move(rowk, colk, r2, c2, speak=False, update=False):
                return False
        print(2, 'ck')
        print('')
        # 3) Recherche d'un coup défensif (capture ou interposition)
        a=(not is_white)
        print(a, "a")
        attackers = self._find_attackers(rowk, colk,a)
        print(attackers, 'attackers')
        # Double échec → mat (seul le roi aurait pu bouger, déjà testé)
        if len(attackers) > 1:
            print('len')
            return True

        # Échec simple : on a exactement un attaquant
        (r_a, c_a) = attackers[0]

        # Construire l'ensemble des cases « cibles » :
        # - la case de l'attaquant (pour le capturer)
        # - si l'attaquant est fou/tour/dame, toutes les cases entre roi et attaquant
        target_sqs = {(r_a, c_a)}

        if self._is_sliding_piece(self.board[r_a, c_a]):
            dr = (r_a - rowk) and ((r_a - rowk) // abs(r_a - rowk))
            dc = (c_a - colk) and ((c_a - colk) // abs(c_a - colk))
            r, c = rowk + dr, colk + dc
            while (r, c) != (r_a, c_a):
                target_sqs.add((r, c))
                r += dr; c += dc
            print('sliding:', target_sqs)
        

        # Pour chaque pièce amie (hors roi), ne tester que les coups vers target_sqs
        for r in range(8):
            for c in range(8):
                piece = self.board[r, c]
                if piece == 0 or (piece > 0) == is_white:
                    continue
                print('gld:', self._generate_legal_destinations(r, c), r, c)
                for (r2, c2) in self._generate_legal_destinations(r, c):
                    if (r2, c2) not in target_sqs:
                        continue
                    # is_valid_move vérifie aussi que le roi ne reste pas en échec
                    if self.is_valid_move(r, c, r2, c2, speak=False, update=False):
                        return False  # coup défensif trouvé
        # Aucun coup défensif => échec et mat
        return True


    def _generate_legal_destinations(self, x: int, y: int):
        """
        Retourne la liste des cases (r2,c2) où la pièce en (x,y) peut
        légalement se déplacer en fonction de son mouvement propre,
        sans tenir compte du fait que cela puisse mettre le roi en échec.
        """
        piece = self.board[x, y]
        dests = []
        kind = abs(piece)
        is_white = piece > 0
        board = self.board

        # 1. Pion
        if kind == 1:
            direction = -1 if is_white else 1
            # Avance d'une case
            nx, ny = x + direction, y
            if (nx in range(8)) and board[nx, ny] == 0:
                dests.append((nx, ny))
                # Avance de deux cases depuis la position initiale
                start_rank = 6 if is_white else 1
                nx2 = x + 2 * direction
                if x == start_rank and board[nx2, ny] == 0:
                    dests.append((nx2, ny))
            # Captures diagonales
            for dy in (-1, 1):
                nx, ny = x + direction, y + dy
                if (nx in range(8)) and (ny in range(8)) and board[nx, ny] != 0:
                    if (board[nx, ny] > 0) != is_white:
                        dests.append((nx, ny))
            # En passant
            for i in [-1, 1]:
                if (self.en_passant['target'] == (x, y+i)):
                    dests.append((x+direction, y+i))

        # 2. Tour et Dame (glissantes orthogonales)
        if kind in (2, 5):
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = x + dx, y + dy
                while (nx in range(8)) and (ny in range(8)):
                    if board[nx, ny] == 0:
                        dests.append((nx, ny))
                    else:
                        if (board[nx, ny] > 0) != is_white:
                            dests.append((nx, ny))
                        break
                    nx += dx; ny += dy

        # 3. Fou et Dame (glissantes diagonales)
        if kind in (4, 5):
            for dx, dy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
                nx, ny = x + dx, y + dy
                while (nx in range(8)) and (ny in range(8)):
                    if board[nx, ny] == 0:
                        dests.append((nx, ny))
                    else:
                        if (board[nx, ny] > 0) != is_white:
                            dests.append((nx, ny))
                        break
                    nx += dx; ny += dy

        # 4. Cavalier
        if kind == 3:
            for dx, dy in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                nx, ny = x + dx, y + dy
                if (nx in range(8)) and (ny in range(8)):
                    if board[nx, ny] == 0 or ((board[nx, ny] > 0) != is_white):
                        dests.append((nx, ny))

        # 5. Roi (y compris roque)
        if kind == 6:
            # Déplacements adjacents
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if (nx in range(8)) and (ny in range(8)) :
                        if board[nx, ny] == 0 or (board[nx, ny] > 0) != is_white:
                            dests.append((nx, ny))
            # Roque
            print('dests:',dests, x, y)
            # petit roque
            if self.is_valid_castling(x, y, y + 2):
                dests.append((x, y + 2))
            print('dests1:',dests)
            # grand roque
            if self.is_valid_castling(x, y, y - 2):
                dests.append((x, y - 2))
            print('dests2:',dests)
        return dests
    

    def  _find_attackers(self, row: int, col: int, is_white="") -> list[tuple[int,int]]:
        """
        Vérifie si la case (row, col) est attaquée par au moins une pièce 
        de la couleur opposée a is_white.
        """
        attackers = []
        board = self.board.copy()
        is_white = board[row, col] > 0 if is_white == "" else is_white
        # --- 1. Attaque par pions ---
        pawn_dirs = [(-1,-1), (-1,1)] if is_white else [(1,-1), (1,1)]
        for dr, dc in pawn_dirs:
            r, c = row + dr, col + dc
            if (r in range(8)) and (c in range(8)):
                if board[r,c] == (-1 if is_white else 1):
                    self.check = (r, c)
                    attackers.append((r,c))
                
         # --- 2. Attaque par cavaliers ---
        knight_offsets = [
            (2,1),(2,-1),(-2,1),(-2,-1),
            (1,2),(1,-2),(-1,2),(-1,-2),
        ]
        for dr, dc in knight_offsets:
            r, c = row+dr, col+dc
            if (r in range(8)) and (c in range(8)):
                if board[r,c] == (-3 if is_white else 3):
                    self.check = (r, c)
                    attackers.append((r,c))

        # --- 3. Attaque par tour / dame (orthogonal) ---
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            r, c = row + dr, col + dc
            while (r in range(8)) and (c in range(8)):
                piece = board[r,c]
                if piece != 0:
                    # si c'est une tour ou une dame adverse
                    if (is_white and piece in (-2, -5)) or ((not is_white) and (piece in (2, 5))):
                        self.check = (r, c)
                        attackers.append((r,c))
                    break
                r += dr; c += dc

        # --- 4. Attaque par fou / dame (diagonales) ---
        for dx, dy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            nx, ny = row + dx, col + dy
            while (nx in range(8)) and (ny in range(8)): 
                piece = board[nx, ny]
                if piece != 0:
                    if (is_white and (piece in (-4, -5))) or ((not is_white) and (piece in (4, 5))):    
                        if (piece > 0) != is_white:
                            attackers.append((nx,ny))
                        break
                    break
                nx += dx; ny += dy

        # --- 5. Attaque par roi (adjacent) ---
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr==0 and dc==0: continue
                r, c = row + dr, col + dc
                if (r in range(8)) and (c in range(8)):
                    if board[r,c] == (-6 if is_white else 6):
                        self.check = (r, c)
                        attackers.append((r,c))

        return attackers
        

    def _is_sliding_piece(self, piece: int) -> bool:
        return abs(piece) in (3, 4, 5)
    

    def is_draw(self, piece=''):
        piece = self.piece if piece == '' else piece 
        # pat
        if self.is_king_in_check(piece):
            if not self.hasLegalMoves(piece):
                return True
        # manque de matériel
        pieces = list(self.board.flatten())
        pieces = [abs(p) for p in pieces if p!=0]
        material = [p for p in pieces if p!=6]
        if all(p for p in [2,3] for p in material) and (len(material) <=2):
            return True
        
    
    def hasLegalMoves(self, piece):
        turn = piece >0
        pieces = list(self.board.flatten())
        pieces = [p for p in pieces if p!=0 and (turn == p>0)]
        for r in range(8):
            for c in range(8):
                if self.board[r, c] in pieces:
                    for p in self._generate_legal_destinations(r, c):
                        r2, c2 = p
                        if self.is_valid_move(r, c, r2, c2, speak=False, update=False):
                            return True
        return False
            
