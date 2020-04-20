from algo_glouton import *

def composantes_connexes(rail_list, rayon, size):
    """Renvoie la liste des composantes connexes, une composante connexe étant représentée par l'ensemble (type set) de ses cases"""
    couverture = rail_list.copy()
    res = []
    while couverture:
        frontiere = set()
        composante_connexe = set()
        frontiere.add(couverture.pop())
        while frontiere:
            (i, j) = frontiere.pop()
            composante_connexe.add((i, j))
            for (k, l) in [(i+1, j), (i-1, j), (i, j+1), (i, j-1), (i+1, j+1), (i-1, j+1), (i+1, j-1), (i-1, j-1)]: # on regarde les voisins (y compris ceux en diagonale)
                if (k, l) in couverture:
                    couverture.remove((k, l))
                    frontiere.add((k, l))
        res.append(composante_connexe)
    return res

def distance_composantes_connexes(composante_a, composante_b):
    """Renvoie la distance entre deux composantes connexes, ainsi que l'endroit où il est atteint"""
    d_carre_min = np.inf
    a_min, b_min = None, None
    for a in composante_a:
        for b in composante_b:
            d_carre = (a[0] - b[0])**2 + (a[1]-b[1])**2
            if d_carre < d_carre_min:
                d_carre_min = d_carre
                a_min, b_min = a, b
    return d_carre_min**0.5, a_min, b_min

def graphe(composantes_connexes):
    """Permet d'associer un graphe  : chaque composante connexe est un sommet, les arêtes sont les chemins les plus courts reliants deux sommets
    Renvoie la matrice d'adjacence des distances entre les sommets et la matrice contenant les coordonnées des arêtes associées"""
    n = len(composantes_connexes)
    mat_adj = np.zeros((n,n), dtype=int)
    aretes = np.full((n,n), None)
    for i in range(1,n):
        for j in range(i):
            d, a, b = distance_composantes_connexes(composantes_connexes[i], composantes_connexes[j])
            mat_adj[i,j] = d
            mat_adj[j,i] = d
            aretes[i,j] = (a, b)
            aretes[j,i] = (b, a)
    return mat_adj, aretes

def arbre_couvrant(mat):
    """Renvoie l'arbre couvrant de poids minimal"""
    n = len(mat)
    visited = set([0])
    not_visited = set(range(1, n))
    res = []
    for _ in range(n-1):
        d_min = np.inf
        arete_min = None
        for s in visited:
            for v in not_visited:
                d = mat[s,v]
                if d < d_min:
                    d_min = d
                    arete_min = (s,v)
        res.append(arete_min)
        _, v = arete_min
        visited.add(v)
        not_visited.remove(v)
    return res

def chemin_ligne(a, b):
    """Renvoie la liste des cases formant un chemin en ligne droite de a à b"""
    a_i, a_j = a
    b_i, b_j = b
    v_i = b_i - a_i
    v_j = b_j - a_j
    norme = (v_i**2 + v_j**2)**0.5
    v_i /= norme
    v_j /= norme
    res = set([a])
    i, j = a_i + 0.5, a_j + 0.5 # On part du centre de la case
    for _ in range(int(norme)):
        i += v_i
        j += v_j
        res.add((int(i), int(j)))
    return res

def connexite_rail_list(mat_adj, aretes):
    """Renvoie l'ensemble des rails fictifs à ajouter pour rendre l'ensemble connexe"""
    res = set()
    for (k, l) in arbre_couvrant(mat_adj):
        a, b = aretes[k,l]
        res = res.union(chemin_ligne(a, b))
    return res