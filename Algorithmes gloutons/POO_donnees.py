from algo_glouton import *
from connexite import *
import pickle
import os
import time

class Donnees_entree(object):
    
    def __init__(self, size=(200,300), rayon=8, background=None, num_antenna_limit=None, cardinalite=1, rail_list=set(), zone_interdite=set(), connexite=False, \
        PSO_nombre_particule=20, PSO_nombre_voisin=5, PSO_c1=0.5, PSO_c2=0.5, PSO_w=0.2):
        """Permet créer un jeu de données initial"""
        self.size = size # Dimensions de la grille
        self.rayon = rayon
        self.background = background # Chaîne de caractère contenant le nom de l'image
        self.num_antenna_limit = num_antenna_limit
        self.cardinalite = cardinalite
        self.rail_list = rail_list
        self.zone_interdite = zone_interdite
        self.connexite = connexite # Si True le calcul du placement d'antennes intègre la contrainte de la connexité
        self.grille = np.zeros(size, dtype=int) # Grille contenant des 1 s'il y a un rail, 0 sinon
        for (i, j) in rail_list:
            self.grille[i][j] = 1
        # Paramètres particule swarm optimization
        self.PSO_nombre_particule = PSO_nombre_particule
        self.PSO_nombre_voisin = PSO_nombre_voisin
        self.PSO_c1 = PSO_c1
        self.PSO_c2 = PSO_c2
        self.PSO_w = PSO_w
    
    def ajout_rail(self, coord):
        """Ajoute un rail à la position coord"""
        self.rail_list.add(coord)
        self.grille[coord[0]][coord[1]] = 1

    def suppression(self, coord):
        """Suppression du rail ou de la zone interdite à la position coord"""
        self.rail_list.discard(coord)
        self.zone_interdite.discard(coord)
        self.grille[coord[0]][coord[1]] = 0   

    def ajout_zone_interdite(self, coord):
        """Ajout d'une zone interdite à la position coord"""
        self.zone_interdite.add(coord)
    
    def save(self, name):
        """Permet de sauvegarder un jeu de données"""
        pickle.dump(self, open("./Sauvegarde données/{}".format(name), "wb"))
    
    def glouton(self, rail_list):
        """Renvoie le résultat de l'algorithme glouton"""
        return MAX_COV(rail_list, self.rayon, self.size, num_antenna_limit=self.num_antenna_limit, zone_interdite=self.zone_interdite, cardinalite=self.cardinalite)
    
    def PSO(self):
        """Renvoie le résultat de l'algorithme PSO"""
        return PSO(self.grille, len(self.rail_list), self.num_antenna_limit, self.rayon, Np = self.nombre_particule, Nv = self.nombre_voisin, psi = self.c1, phi = self.c2, \
            omega = self.w)
    
def load(name):
    """Permet de charger une instance de données"""
    if not name in os.listdir("./Sauvegarde données/"):
        return None
    else:
        return pickle.load(open("./Sauvegarde données/{}".format(name), 'rb'))

class Donnees_sortie(object):

    def __init__(self, entree, algo):
        self.entree = entree # Données d'entrée, de classe : Donnees_entree
        self.algo = algo # Chaine de caractère de l'algo utilisé

        # Calculs liés à la connexité
        if entree.connexite:
            t0 = time.time()
            self.cc = composantes_connexes(entree.rail_list, entree.rayon, entree.size) # cc pour composantes connexes
            self.nbr_cc = len(self.cc)
            self.connexe = self.nbr_cc == 1
            self.mat_adj, self.aretes = graphe(self.cc)
            self.choix_aretes = arbre_couvrant(self.mat_adj)
            self.rails_fictifs = connexite_rail_list(self.mat_adj, self.aretes)
            self.rail_connexite = entree.rail_list.union(self.rails_fictifs) # Ensemble des rails à prendre en compte lorsqu'on intègre la contrainte de la connexité
            self.temps_connexite = time.time() - t0
            
        # Calcul du placement d'antennes
        t0 = time.time()
        if algo == "glouton":
            if entree.connexite:
                rail_list = self.rail_connexite
            else:
                rail_list = entree.rail_list
            self.liste_antennes, self.taux_couverture = entree.glouton(rail_list)
        else:
            raise ValueError("algo non reconnu")
        self.temps_execution = time.time() - t0
        self.nombre_antennes = len(self.liste_antennes)