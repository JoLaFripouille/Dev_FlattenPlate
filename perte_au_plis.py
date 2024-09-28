import customtkinter as ctk
import json
import tkinter as tk
import numpy as np
import matplotlib
import os
import ezdxf
import scipy
import PIL
from PIL import Image
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, messagebox

# Charger l'image (assurez-vous que l'image "copy.png" est dans le dossier "img")
image_copier = image_copier = ctk.CTkImage(light_image=Image.open("img/copy.png"), dark_image=Image.open("img/copyL.png"), size=(24, 24))

matplotlib.use('TkAgg')  # Utilise le backend Tkinter au lieu de Qt

def ouvrir_dossier():
    dossier = filedialog.askdirectory()
    if dossier:
        label_chemin_dossier.configure(text=dossier)

def generer_dxf(hauteur, largeur, bouleen, chemin_dossier, nom_fichier):
    """
    Génère un fichier DXF contenant un rectangle de dimensions spécifiées.
    Optionnellement, ajoute deux cercles de diamètre 3.5 aux coins supérieurs
    gauche et droit du rectangle, à une distance de 5 unités des bords.

    Paramètres:
    - hauteur (float): Hauteur du rectangle.
    - largeur (float): Largeur du rectangle.
    - bouleen (bool): Si True, ajoute les deux cercles au rectangle.
    - chemin_dossier (str): Chemin vers le dossier où le fichier DXF sera enregistré.
    - nom_fichier (str): Nom du fichier DXF (doit se terminer par '.dxf').

    Retour:
    - Aucun
    """
    # Vérifie que le dossier existe, sinon le crée
    if not os.path.exists(chemin_dossier):
        os.makedirs(chemin_dossier)

    # Vérifie que le nom du fichier se termine par '.dxf'
    if not nom_fichier.lower().endswith('.dxf'):
        nom_fichier += '.dxf'

    # Crée un nouveau document DXF
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()

    # Trace le rectangle
    points = [(0, 0), (largeur, 0), (largeur, hauteur), (0, hauteur), (0, 0)]
    msp.add_lwpolyline(points, close=True)

    # Ajoute les cercles si bouleen est True
    if bouleen:
        rayon = 1.75  # Diamètre 3.5 divisé par 2
        # Centre du cercle gauche
        centre_gauche = (5, hauteur - 5)
        # Centre du cercle droit
        centre_droit = (largeur - 5, hauteur - 5)
        msp.add_circle(centre_gauche, rayon)
        msp.add_circle(centre_droit, rayon)

    # Enregistre le fichier DXF
    chemin_complet = os.path.join(chemin_dossier, nom_fichier)
    doc.saveas(chemin_complet)



def fermer_fenetre():
    root.quit()  # Arrête la boucle principale de tkinter
    root.destroy()  # Détruit la fenêtre proprement

# Charger les données des matériaux
def charger_donnees_materiau(nom_fichier):
    with open(nom_fichier, 'r') as f:
        return json.load(f)

# Calculer la longueur finale en tenant compte de la perte au pli
def calculer_longueur_finale(longueur_initiale, angles_pli, spline):
    perte_totale = sum(spline(angle) for angle in angles_pli)
    longueur_finale = longueur_initiale - perte_totale
    return longueur_finale

# Fonction pour mettre à jour l'interface avec les champs pour les angles
def demander_angles(*args):
    try:
        
        nombre_de_plis = int(entry_nombre_plis_var.get())  # Essayer de convertir en entier

        # Si la conversion réussit, on continue
        for widget in frame_angles.winfo_children():
            widget.destroy()

        angles_pli.clear()  # Effacer les angles précédents
        for i in range(nombre_de_plis):
            label_angle = ctk.CTkLabel(frame_angles, text=f"Angle du pli {i+1}:")
            label_angle.grid(row=i, column=0, padx=10, pady=10)

            entry_angle = ctk.CTkEntry(frame_angles)
            entry_angle.grid(row=i, column=1, padx=10, pady=10)
            angles_pli.append(entry_angle)

        frame_longueur.pack(pady=10, padx=10)
    
    except ValueError:
        # Si la conversion échoue (pas un entier), on ignore l'erreur
        pass

# Fonction pour copier la valeur dans le presse-papiers et afficher la notification animée
def copier_texte_au_presse_papiers():
    root.clipboard_clear()  # Vider le presse-papiers
    valeur = longueur_finale  # Valeur à copier dans le presse-papiers
    root.clipboard_append(valeur)  # Ajouter la valeur au presse-papiers

    # Créer une petite frame temporaire en haut à gauche de root
    frame_popup = ctk.CTkFrame(root, width=250, height=30, corner_radius=15, border_width=2)
    label_popup = ctk.CTkLabel(frame_popup,height=20, text=f" '{valeur:.2f}' copié dans le presse-papiers")
    label_popup.pack(pady=5, padx=20)

    # Fonction pour animer l'entrée par le haut
    def entrer_par_le_haut(y=0):
        if y <= 10:  # La position finale en y est 10
            frame_popup.place(x=10, y=y)
            root.after(10, entrer_par_le_haut, y+1)  # Déplacer de 5 pixels à chaque itération
        else:
            root.after(2000, glisser_vers_la_gauche)  # Attendre 2 secondes avant de faire glisser la fenêtre

    # Fonction pour animer la sortie vers la gauche
    def glisser_vers_la_gauche(x=10):
        if x >= -210:  # La frame doit disparaître en sortant de l'écran (largeur de la frame = 200)
            frame_popup.place(x=x, y=10)
            root.after(10, glisser_vers_la_gauche, x-6)  # Déplacer de 5 pixels vers la gauche à chaque itération
        else:
            frame_popup.destroy()  # Détruire la frame après qu'elle ait disparu

    # Démarrer l'animation par le haut
    entrer_par_le_haut()

    
# Fonction pour calculer et afficher le résultat
def calculer_resultat():
    
    global longueur_finale
    
    frame_resultat.pack(pady=10, padx=10)
    
    try:
        materiau = combobox_materiau.get()
        angles = np.array(donnees_materiaux[materiau]["angles"])
        developes = np.array(donnees_materiaux[materiau]["developes"])

        # Calculer la perte au pli
        pertes = 100 - developes  # Perte = 100 - Développement

        # Trier les angles et pertes
        angles_sorted = np.sort(angles)
        pertes_sorted = pertes[np.argsort(angles)]

        # Interpolation par spline cubique pour la perte
        spline = CubicSpline(angles_sorted, pertes_sorted)

        # Récupérer les valeurs d'angles saisies
        angles_values = [float(entry.get()) for entry in angles_pli]
        expression = entry_longueur_initiale.get()
        result = eval(expression)
        longueur_initiale = float(result)

        longueur_finale = calculer_longueur_finale(longueur_initiale, angles_values, spline)
        label_resultat.configure(text=f"Développé :  {longueur_finale:.2f} mm")

        # Générer les points pour tracer la spline
        angle_fit = np.linspace(min(angles_sorted), max(angles_sorted), 500)
        perte_spline = spline(angle_fit)

        # Calculer les pertes pour les angles entrés par l'utilisateur
        pertes_values = spline(angles_values)
        
        

        afficher_graphique(angles_sorted, pertes_sorted, angle_fit, perte_spline, angles_values, pertes_values)
    except Exception as e:
        label_resultat.configure(text=f"Erreur: {str(e)}")

# Fonction pour afficher le graphique avec la spline cubique de la perte et les points saisis en jaune
def afficher_graphique(angles_sorted, pertes_sorted, angle_fit, perte_spline, angles_values, pertes_values):
    fig, ax = plt.subplots(figsize=(4, 4))

    # Tracer les points d'origine (perte au pli)
    ax.scatter(angles_sorted, pertes_sorted, color='blue', label="Perte au pli (bleu)")

    # Tracer la spline cubique pour la perte
    ax.plot(angle_fit, perte_spline, color='green', label="Spline cubique (perte)")

    # Tracer les points des angles entrés par l'utilisateur en jaune
    ax.scatter(angles_values, pertes_values, color='red', label="Points saisis (rouge)", zorder=5)

    ax.set_xlabel('Angle (degrés)')
    ax.set_ylabel('Perte au pli (mm)')
    ax.set_title('Perte au pliage en fonction de l\'angle')
    ax.grid(True)
    ax.legend()

    # Intégration du graphique dans l'interface
    for widget in frame_graphique.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame_graphique)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Fonction pour charger et afficher le graphique dès le démarrage
def afficher_premiere_matiere():
    premiere_matiere = combobox_materiau.get()
    angles = np.array(donnees_materiaux[premiere_matiere]["angles"])
    developes = np.array(donnees_materiaux[premiere_matiere]["developes"])

    # Calcul de la perte au pli
    pertes = 100 - developes  # Perte = 100 - Développement

    angles_sorted = np.sort(angles)
    pertes_sorted = pertes[np.argsort(angles)]
    
    # Interpolation par spline cubique pour la perte
    spline = CubicSpline(angles_sorted, pertes_sorted)

    # Générer les points pour la spline
    angle_fit = np.linspace(min(angles_sorted), max(angles_sorted), 500)
    perte_spline = spline(angle_fit)

    # Afficher le graphique de la perte au pli
    afficher_graphique(angles_sorted, pertes_sorted, angle_fit, perte_spline, [], [])

# Chargement des données des matériaux
donnees_materiaux = charger_donnees_materiau("data.json")
angles_pli = []

# Initialisation de la fenêtre principale
root = ctk.CTk()
root.title("Calcul de Développé avec Perte au Pli")
root.geometry("750x590")
root.resizable(False,False)
root.protocol("WM_DELETE_WINDOW", fermer_fenetre)

# Créer une variable pour surveiller les changements dans l'entrée "Nombre de plis"
entry_nombre_plis_var = tk.StringVar()
entry_nombre_plis_var.trace("w", demander_angles)  # Appeler demander_angles à chaque changement

frame_principal = ctk.CTkFrame(root, width=450, corner_radius=10)
frame_principal.place(x=15+320+15, y=15)

frame_graphique = ctk.CTkFrame(root)
frame_graphique.place(x=15, y=15)

frame_DXF = ctk.CTkFrame(root, width=320,height=235,corner_radius=15)
frame_DXF.place(x=15, y=15+320+15)

frame_DXF_largeur = ctk.CTkFrame(frame_DXF, width=320,height=230,corner_radius=15)
frame_DXF_largeur.place(x=10,y=10)

label_longueur = ctk.CTkLabel(frame_DXF_largeur, text="Longueur:")
label_longueur.pack(side='left',pady=10,padx=5)
entry_largeur = ctk.CTkEntry(frame_DXF_largeur)
entry_largeur.pack(pady=10,padx=10)
var_bouleen = ctk.BooleanVar()
checkbox_bouleen = ctk.CTkCheckBox(frame_DXF, text="Ajouter des percages pour suspendre", variable=var_bouleen)
checkbox_bouleen.place(x=15,y=10+30+28)

frame_chemin_dossier = ctk.CTkFrame(frame_DXF,width=320,height=210,corner_radius=15)
frame_chemin_dossier.place(x=10,y=10+30+28*2+5)

label_chemin_dossier = ctk.CTkLabel(frame_chemin_dossier, text="Aucun dossier sélectionné", anchor="w")
label_chemin_dossier.pack(side="bottom", padx=1,pady=3)
bouton_parcourir = ctk.CTkButton(frame_chemin_dossier,width=200, text="Parcourir", command=ouvrir_dossier)
bouton_parcourir.pack(side="top", padx=48, pady=5)
btn_generate_DXF = ctk.CTkButton(frame_DXF, text="Generer le fichier DXF",width=300,height=42,corner_radius=15,fg_color='transparent',border_width=2,font=("Helvetica",16))
btn_generate_DXF.place(x=10,y=10+50+28*4+10)

btn_DXF = ctk.CTkButton(root, text="Generer un fichier DXF", height=235, width=320,corner_radius=15,fg_color='transparent',border_width=2,font=("Helvetica",20))
#btn_DXF.place(x=15, y=15+320+15)

# Frame pour la sélection du matériau
frame_materiau = ctk.CTkFrame(frame_principal)
frame_materiau.pack(pady=10, padx=20)

label_materiau = ctk.CTkLabel(frame_materiau, text="Sélectionnez la matière:")
label_materiau.grid(row=0, column=0, padx=10, pady=7)

combobox_materiau = ctk.CTkComboBox(frame_materiau, width=170, values=list(donnees_materiaux.keys()))
combobox_materiau.grid(row=0, column=1, padx=10, pady=5)
combobox_materiau.set(list(donnees_materiaux.keys())[0])  # Sélectionner automatiquement la première matière

# Frame pour entrer le nombre de plis
frame_nombre_plis = ctk.CTkFrame(frame_principal)
frame_nombre_plis.pack(pady=10, padx=10)

label_nombre_plis = ctk.CTkLabel(frame_nombre_plis, text="Nombre de plis:")
label_nombre_plis.grid(row=0, column=0, padx=15, pady=7)

# Lier la variable à l'entrée "Nombre de plis"
entry_nombre_plis = ctk.CTkEntry(frame_nombre_plis, textvariable=entry_nombre_plis_var)
entry_nombre_plis.grid(row=0, column=1, padx=10, pady=7)

# Frame pour entrer les angles de chaque pli
frame_angles = ctk.CTkScrollableFrame(frame_principal, width=285)
frame_angles.pack(pady=10)

# Frame pour entrer la longueur initiale
frame_longueur = ctk.CTkFrame(frame_principal, width=350)

label_longueur_initiale = ctk.CTkLabel(frame_longueur, text="Somme des cotes exterieur:")
label_longueur_initiale.grid(row=0, column=0, padx=10, pady=10)

entry_longueur_initiale = ctk.CTkEntry(frame_longueur)
entry_longueur_initiale.grid(row=0, column=1, padx=10, pady=10)

btn_calculer = ctk.CTkButton(frame_longueur, text="Calculer", command=calculer_resultat)
btn_calculer.grid(row=1, column=0, columnspan=2, pady=10)

# Frame pour afficher le résultat
frame_resultat = ctk.CTkFrame(frame_principal,border_width=2, corner_radius=20, border_color='white')

label_resultat = ctk.CTkLabel(frame_resultat, text="", font=("Helvetica", 18),corner_radius=10)
label_resultat.grid(row=0,column=0,padx=10,pady=5)

btn_copier = ctk.CTkButton(frame_resultat,width=36,height=36,image=image_copier,corner_radius=15, text="", fg_color='transparent', command=copier_texte_au_presse_papiers)
btn_copier.grid(row=0,column=1,pady=5, padx=9)




# Afficher le graphique de la première matière lors du démarrage
afficher_premiere_matiere()

root.mainloop()
