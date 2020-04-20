from pytest import *
from algo_glouton import *
import random

def placement_aleatoire(rail_list, rayon, size, num_antenna_limit):
    """Renvoie la liste des positions des antennes selon le procédé suivant :
    On tire une antenne au hasard dans la liste des rails non couverts jusqu'à ce que la couverture soit totale"""

    # Initialisation
    L = rail_list.copy() # liste des rails non couverts
    num_sensors = 0 # compteur du nombre d'antennes posées
    res = [] # résultat : liste des positions des antennes

    # Traitement
    while L and (num_antenna_limit == None or num_sensors <= num_antenna_limit):
        (i, j) = random.choice(list(L)) # selection au hasard d'une nouvelle antenne
        res.append((i, j))
        num_sensors += 1
        if len(L) < (2*rayon + 1)**2: # 2 méthodes suivant qu'il soit plus rapide de parcourir L ou le carré contenant le disque de l'antenne posée
            l_couverte = [a for a in L if portee(a, (i, j),rayon)] # liste des rails qui n'étaient pas couverts et qui sont couverts par la nouvelle antenne
        else:
            l_couverte = []
            for k in range(max(0, i-rayon), min(size[0], i+rayon+1)):
                for l in range(max(0, j-rayon), min(size[1], j+rayon+1)):
                    if portee((i, j), (k, l), rayon) and (k, l) in L:
                        l_couverte.append((k, l))
        for rail_pos in l_couverte:
            L.remove(rail_pos) # on retire les antennes couvertes

    return res

def test_portee():
    """Test de la fonction portee"""
    a = (0,0)
    b = (3,4) # distance(a,b) = 5 + 1/2**0.5
    assert not portee(a, b, 4)
    assert portee(a, b, 6)

def test_cherche_max():
    """Test de la fonction cherche_max"""
    M = [[5, 4, 3], [7, 1, 2]]
    assert cherche_max(M) == [(1,0)]


def test_MAX_COV():
    """Test de la fonction MAX_COV, comparaison avec l'algo de placement aléatoire d'antennes, on regarde si le nombre d'antennes que renvoie MAX_COV est plus faible que si on place les antennes au hasard sur le chemin de fer"""
    size = (100,100)
    rayon = 5
    num_antenna_limit = 500
    # chemin de fer vertical
    rail_list = set([(i, j) for i in range(size[0]) for j in range(size[1]) if j == 10])
    res, taux_couverture = MAX_COV(rail_list, rayon, size, num_antenna_limit=num_antenna_limit, zone_interdite=set())
    assert len(res) <= len(placement_aleatoire(rail_list, rayon, size, num_antenna_limit))
    assert taux_couverture == 1
    # chemin de fer horizontal
    rail_list = set([(i, j) for i in range(size[0]) for j in range(size[1]) if i == 4])
    res, taux_couverture = MAX_COV(rail_list, rayon, size, num_antenna_limit=num_antenna_limit, zone_interdite=set())
    assert len(res) <= len(placement_aleatoire(rail_list, rayon, size, num_antenna_limit))
    assert taux_couverture == 1
    # chemin de fer en croix
    rail_list = set([(i, j) for i in range(size[0]) for j in range(size[1]) if i == j or i + j == size[0]])
    res, taux_couverture = MAX_COV(rail_list, rayon, size, num_antenna_limit=num_antenna_limit, zone_interdite=set())
    assert len(res) <= len(placement_aleatoire(rail_list, rayon, size, num_antenna_limit))
    assert taux_couverture == 1
    # chemin de fer généré aléatoirement
    rail_list = set([(random.randint(0, size[0]-1), random.randint(0, size[1]-1)) for _ in range(200)])
    res, taux_couverture = MAX_COV(rail_list, rayon, size, num_antenna_limit=num_antenna_limit, zone_interdite=set())
    assert len(res) <= len(placement_aleatoire(rail_list, rayon, size, num_antenna_limit))
    assert taux_couverture == 1
