import numpy as np

"""
Algorithme inspiré de l'article de Santpal « Sensor Placement for Effective Coverage … »

Principe:
- On découpe la carte en grille, et on regarde sur quelles cases passe le chemin de fer
- On place une nouvelle antenne sur la case qui maximise le nombre d'antennes non encore couvertes
"""

#Implémentation de fonctions auxiliaires

def portee(a, b, d_max):
    """Renvoie True si la distance entre a et b est inférieure ou égale à d_max"""
    return (a[0] - b[0])**2 + (a[1]-b[1])**2 <= (d_max - 1 / 2**0.5)**2 # Le - 1 / 2**0.5 vient du fait qu'on souhaite que la totalité du carré soit dans le cercle 

def cherche_max(M):
    """Renvoie les coordonnées du maximum d'une matrice"""
    val_max = M[0][0]
    liste_position = []
    for i in range(len(M)):
        for j in range(len(M[0])):
            val = M[i][j]
            if val == val_max:
                liste_position.append((i,j))
            if val > val_max:
                val_max = val
                liste_position = [(i, j)]
    return liste_position

def disque(centre, rayon, size):
    """Renvoie la liste des positions des cases situées dans le disque (éventuellement tronqué sur les côtés)"""
    return [(i, j) for i in range(max(0, centre[0]-rayon), min(size[0], centre[0]+rayon+1)) \
                   for j in range(max(0, centre[1]-rayon), min(size[1], centre[1]+rayon+1)) \
                   if portee((i, j), centre, rayon)]

def traitement_cas_egalite(liste_position, rayon, size, L):
    """La recherche du max de sigma peut aboutir à plusieurs résultats ; afin de choisir le meilleur, nous allons regarder la somme des distances au carré avec les rails couverts.
    La fonction renvoie le min, avec sa liste des rails couverts"""
    l_couverte = {} # à chaque position probable associe la liste des rails couverts
    somme_distances_carres = {} # à chaque position probable associe la somme des distances au carré avec les rails couverts
    for (i, j) in liste_position:
        if len(L) < (2*rayon + 1)**2: # 2 méthodes suivant qu'il soit plus rapide de parcourir L ou le carré contenant le disque de l'antenne posée
            l_couverte[(i, j)] = [a for a in L if portee(a, (i, j),rayon)] # liste des rails qui n'étaient pas couverts et qui sont couverts par la nouvelle antenne
        else:
            l_couverte[(i, j)] = []
            for (k, l) in disque((i, j), rayon, size):
                if (k, l) in L:
                    l_couverte[(i, j)].append((k, l))
        somme_distances_carres[(i, j)] = sum([(i-k)**2 + (j-l)**2 for (k, l) in l_couverte[(i, j)]])
    # Recherhce du minimum
    cle_min, val_min = None, np.inf
    for cle in somme_distances_carres:
        val = somme_distances_carres[cle]
        if val < val_min:
            cle_min, val_min = cle, val
    return cle_min, l_couverte[cle_min]

#Implémentation des fonctions de placement d'antennes

def MAX_COV(rail_list, rayon, size, num_antenna_limit=None, zone_interdite=[], cardinalite=1):
    """Renvoie la liste des positions des antennes
    Entrée :
    - rail_list : liste des positions des cases où passe le chemin de fer
    - rayon : rayon de l'antenne (1 unité de distance = 1 côté d'une case)
    - size : tuple qui indique la taille de la grille (nombre de lignes, nombre de colonnes)
    - num_antenna_limit : nombre maximal d'antennes à poser avant que l'algorithme ne s'arrête, si None: pas de limite
    - zone_interdite : liste des positions des cases où on ne peut pas placer d'antennes (zone d'habitation, centrale nucléaire...)
    - cardinalite : chaque rail doit être couvert par un nombre minimum d'antennes, appelé cardinalité
    Sortie : liste des positions des antennes, taux de couverture"""

    # Initialisation
    L = {rail: cardinalite for rail in rail_list} # liste des rails non couverts
    sigma = np.zeros(size, dtype=int) # matrice qui à chaque case de la grille associe le nombre d'antennes couvertes si on place une antenne sur cette case
    for rail_pos in rail_list:
        for (i, j) in disque(rail_pos, rayon, size):
            sigma[i,j] += 1
    for (i, j) in zone_interdite:
        sigma[i, j] = 0 # on fixe la valeur à 0 afin que la case ne puisse pas être choisie lors de la recherche du maximum de sigma
    num_sensors = 0 # compteur du nombre d'antennes posées
    res = [] # résultat : liste des positions des antennes

    # Traitement
    while L and (num_antenna_limit == None or num_sensors <= num_antenna_limit):

        # Sélection de la nouvelle antenne
        liste_position = cherche_max(sigma) # on cherche la liste des positions des antennes pour lesquelles sigma est maximale
        if sigma[liste_position[0]] <= 0: # avec la mise en place de zones interdites, il se peut que certains rails ne puissent pas être couvert par une antenne
            break
        (i, j), l_couverte = traitement_cas_egalite(liste_position, rayon, size, L) # on selectionne la meilleur position
        
        # Mise à jour des variables
        res.append((i, j))
        num_sensors += 1
        sigma[i][j] = 0 # pour que la case (i,j) ne soit plus choisie pour remettre une antenne
        for rail_pos in l_couverte:
            L[rail_pos] -= 1 # on décrémente le nombre d'antennes nécessaires pour que rail_pos soit couvert
            if L[rail_pos] == 0: # le rail est totalement couvert
                del L[rail_pos] # on retire les antennes couvertes
                for (k, l) in disque(rail_pos, rayon, size):
                    sigma[k,l] -= 1 # on met à jour sigma, en retirant les rails couverts par la nouvelle antenne
    
    # Calcul du taux de couverture
    if len(rail_list) == 0:
        taux_couverture = None
    else:
        taux_couverture = (len(rail_list) - len(L)) / len(rail_list)
    
    return res, taux_couverture