from POO_donnees import *
import pygame
from pygame.locals import *
import os

def affichage(data, sortie, fenetre, affichage_connexite):
    """Représentation de la grille avec les rails, les antennes et leur portée"""
    # rayon += math.sqrt(2) #pour que ce soit plus jolie
    w, h = pygame.display.get_surface().get_size() # dimension de la fenêtre (en pixels)
    width, height = w // data.size[1], h // data.size[0] # taille des cases (en pixels)
    
    # Placement des rectangles verts représentant les zones interdites
    for (i,j) in data.zone_interdite:
        left, top = j*width, i*height
        pygame.draw.rect(fenetre, (0,255,0), Rect(left, top, width, height))

    # Placement des cercles rouges représentant la portée des antennes
    for (i,j) in sortie.liste_antennes:
        left, top = (j+0.5)*width, (i+0.5)*height # On part des coordonnées du centre du rectangle
        left, top = left - width*data.rayon, top - height*data.rayon # On veut le coin supérieur gauche du rectangle
        left, top = int(left), int(top)
        pygame.draw.ellipse(fenetre, (255,0,0), Rect(left, top, int((2*width)*data.rayon), int((2*height)*data.rayon), width=0))

    # Affichage des chemins fictifs pour la contrainte de la connexité
    if data.connexite and affichage_connexite:
        # rectangles jaunes pour les rails fictifs
        for (i,j) in sortie.rails_fictifs:
            left, top = j*width, i*height
            pygame.draw.rect(fenetre, (255,255,0), Rect(left, top, width, height))
        # lignes noirs reliant les composantes connexes
        for k, l in sortie.choix_aretes:
            a, b = sortie.aretes[k,l]
            start_point = (a[1] + 0.5)*width, (a[0] + 0.5)*height
            end_point = (b[1] + 0.5)*width, (b[0] + 0.5)*height
            pygame.draw.line(fenetre, (0,0,0), start_point, end_point)

    # Placement des rectangles noirs représentant les rails
    for (i,j) in data.rail_list:
        left, top = j*width, i*height
        pygame.draw.rect(fenetre, (0,0,0), Rect(left, top, width, height))
    
    # Placement des rectangles bleus représentant les antennes
    for (i,j) in sortie.liste_antennes:
        left, top = j*width, i*height
        pygame.draw.rect(fenetre, (0,0,255), Rect(left, top, width, height))        


def anim_pygame(algo, data=Donnees_entree(), dim_horizontale_fen=1300):
    """Permet de créer des instances de données et de visualiser la solution
    Les fonctionnalités :
    - clic gauche : placement d'un tronçon de rail
    - clic molette : placement d'une zone interdite
    - clic droit : effaçage d'un rail ou d'une zone interdite
    - espace : calcul du placement d'antennes
    - s (save): sauvegarde des données d'entrée, interagir avec la console
    - l (load): chargement des données d'entrée, interagir avec la console
    - c (connexité): affichage ou masquage des chemins fictifs pour la contrainte de la connexité"""
    
    #Initialisation de pygame
    pygame.init()

    #Calcul des dimensions de la fenêtre
    if data.background != None: # on veut que la fenêtre garde les dimensions de l'image pour ne pas la déformer
        fenetre = pygame.display.set_mode((1, 1)) # on doit ouvrir une fenêtre pour charger l'image afin de récupérer ses dimensions
        fond = pygame.image.load("./Images de fond/{}".format(data.background)).convert() # chargement de l'image de fond
        w , h = fond.get_size() # dimensions de l'image
        dim_verticale_fen = int(dim_horizontale_fen * h / w)
        dim_horizontale_fen //= data.size[1] # pour avoir un nombre fixe et entier de pixels par case on doit arrondir 
        dim_verticale_fen //= data.size[0] # pour avoir un nombre fixe et entier de pixels par case on doit arrondir
        dim_horizontale_fen *= data.size[1] # nombre de pixels de la fenêtre en horizontale
        dim_verticale_fen *= data.size[0] # nombre de pixels de la fenêtre en verticale
        fond = pygame.transform.scale(fond, (dim_horizontale_fen, dim_verticale_fen)) #ajustement de la taille de l'image de fond
    else: # on veut que la fenêtre prenne les dimensions indiquées par size et que les cases soient des carrés
        r = dim_horizontale_fen // data.size[1] # pour avoir un nombre fixe et entier de pixels par case on doit arrondir
        dim_horizontale_fen = r * data.size[1]
        dim_verticale_fen = r * data.size[0]
    
    #Ouverture de la fenêtre
    fenetre = pygame.display.set_mode((dim_horizontale_fen, dim_verticale_fen))

    #Settings
    pygame.key.set_repeat(1, 1) #Quand on garde la touche enfoncée on est en KEYDOWN
    font = pygame.font.SysFont(None, 24) # permet d'écrire du texte

    #Initiation des données
    sortie = Donnees_sortie(data, algo)
    affichage_connexite = False
    w, h = pygame.display.get_surface().get_size()
    width, height = w // data.size[1], h // data.size[0] #taille en pixels d'un côté d'une case

    #Affichage
    if data.background != None:
        fenetre.blit(fond, (0,0)) # on met l'image en fond
    else:
        fenetre.fill((255,255,255)) # fond blanc
    affichage(data, sortie, fenetre, affichage_connexite)
    pygame.display.flip()
    
    #BOUCLE INFINIE
    continuer = 1
    while continuer:

        # Modification de la grille
        for event in pygame.event.get():
            # Fermeture de la fenêtre
            if event.type == QUIT: # On clique sur la croix
                continuer = 0
            # Calcul du placement d'antennes
            if event.type == KEYDOWN and event.key == K_SPACE: # On appuie sur espace
                sortie = Donnees_sortie(data, algo)
            # Affichage des chemins fictifs pour la contrainte de connexité
            if event.type == KEYUP and event.key == K_c: # On appuie sur c (connexite)
                affichage_connexite = not affichage_connexite
            # Sauvegarde du jeu de données
            if event.type == KEYDOWN and event.key == K_s: # On appuie sur s (save)
                name = input("Nom de sauvegarde : ")
                while name in os.listdir("./Sauvegarde données/"):
                    if input("Ce nom est déjà attribué à un jeu de données, voulez vous le remplacer ? Y/N ").lower() in ["y", "yes", "oui"]:
                        break
                    else:
                        name = input("Nouveau nom de sauvegarde : ")
                data.save(name)
                print("Le jeu de sonnées a bien été sauvegardé.")
            # Chargement d'un jeu de données
            if event.type == KEYDOWN and event.key == K_l: # On appuie sur l (load)
                name = input("Nom du jeu de donné à charger parmi {} : ".format(os.listdir("./Sauvegarde données/")))
                d = load(name)
                if d == None:
                    print("Ce nom n'est pas dans la liste, les données n'ont pas été chargées.")
                else:
                    data = d
                    print("Le jeu de données a été chargé.")
        mouse = pygame.mouse.get_pressed()
        x, y = pygame.mouse.get_pos()
        i, j = y // height, x // width
        if i < data.size[0] and j < data.size[1]:
            if mouse[0]: # si clic gauche
                data.ajout_rail((i, j))
            elif mouse[2]: # si clic droit
                data.suppression((i, j))
            elif mouse[1]: # si clic molette
                data.ajout_zone_interdite((i, j))
        
        # Affichage de la grille
        if data.background != None:
            fenetre.blit(fond, (0,0))
        else:
            fenetre.fill((255,255,255)) # fond blanc
        affichage(data, sortie, fenetre, affichage_connexite)
        if sortie.taux_couverture == None:
            texte = ""
        else:
            texte = "Couverture : {} %".format(int(sortie.taux_couverture * 100))
        fenetre.blit(font.render(texte, True, (0, 128, 0)), (0, 0)) # affichage du texte
        pygame.display.flip()

def main():
    anim_pygame("glouton", Donnees_entree(background="Ile_de_France.jpg", connexite=True))

if __name__== "__main__":
    main()