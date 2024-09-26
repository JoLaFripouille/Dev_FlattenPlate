import customtkinter as ctk
import json
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Utilise le backend Tkinter au lieu de Qt
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
def demander_angles():
    frame_angles.pack(pady=10)
    nombre_de_plis = int(entry_nombre_plis.get())
    
    for widget in frame_angles.winfo_children():
        widget.destroy()
    
    angles_pli.clear()  # Clear previous angles
    for i in range(nombre_de_plis):
        label_angle = ctk.CTkLabel(frame_angles, text=f"Angle du pli {i+1}:")
        label_angle.grid(row=i, column=0, padx=10, pady=5)
        
        entry_angle = ctk.CTkEntry(frame_angles)
        entry_angle.grid(row=i, column=1, padx=10, pady=5)
        angles_pli.append(entry_angle)
    
    frame_longueur.pack(pady=10,padx=10)

# Fonction pour calculer et afficher le résultat
def calculer_resultat():
    frame_resultat.pack(pady=10)
    
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
        longueur_initiale = float(entry_longueur_initiale.get())

        longueur_finale = calculer_longueur_finale(longueur_initiale, angles_values, spline)
        label_resultat.configure(text=f"Longueur Développé (avec perte):  {longueur_finale:.2f} mm")

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
    fig, ax = plt.subplots(figsize=(5, 4))

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
root.geometry("900x500")
root.protocol("WM_DELETE_WINDOW", fermer_fenetre)



frame_principal = ctk.CTkFrame(root)
frame_principal.grid(row=0, column=1, padx=10, pady=15)

frame_graphique = ctk.CTkFrame(root)
frame_graphique.grid(row=0, column=0, padx=10, pady=15)

# Frame pour la sélection du matériau
frame_materiau = ctk.CTkFrame(frame_principal)
frame_materiau.pack(pady=10, padx=10)

label_materiau = ctk.CTkLabel(frame_materiau, text="Sélectionnez la matière:")
label_materiau.grid(row=0, column=0, padx=10, pady=5)

combobox_materiau = ctk.CTkComboBox(frame_materiau, values=list(donnees_materiaux.keys()))
combobox_materiau.grid(row=0, column=1, padx=10, pady=5)
combobox_materiau.set(list(donnees_materiaux.keys())[0])  # Sélectionner automatiquement la première matière

# Frame pour entrer le nombre de plis
frame_nombre_plis = ctk.CTkFrame(frame_principal)
frame_nombre_plis.pack(pady=10)

label_nombre_plis = ctk.CTkLabel(frame_nombre_plis, text="Nombre de plis:")
label_nombre_plis.grid(row=0, column=0, padx=10, pady=5)

entry_nombre_plis = ctk.CTkEntry(frame_nombre_plis)
entry_nombre_plis.grid(row=0, column=1, padx=10, pady=5)

btn_valider_nombre_plis = ctk.CTkButton(frame_nombre_plis, text="Entrer", command=demander_angles)
btn_valider_nombre_plis.grid(row=1, column=0, columnspan=2, pady=10)

# Frame pour entrer les angles de chaque pli
frame_angles = ctk.CTkFrame(frame_principal)

# Frame pour entrer la longueur initiale
frame_longueur = ctk.CTkFrame(frame_principal)

label_longueur_initiale = ctk.CTkLabel(frame_longueur, text="Somme des cotes exterieur:")
label_longueur_initiale.grid(row=0, column=0, padx=10, pady=5)

entry_longueur_initiale = ctk.CTkEntry(frame_longueur)
entry_longueur_initiale.grid(row=0, column=1, padx=10, pady=5)

btn_calculer = ctk.CTkButton(frame_longueur, text="Calculer", command=calculer_resultat)
btn_calculer.grid(row=1, column=0, columnspan=2, pady=10)

# Frame pour afficher le résultat
frame_resultat = ctk.CTkFrame(frame_principal)

label_resultat = ctk.CTkLabel(frame_resultat, text="", font=("Helvetica", 18))
label_resultat.pack()




# Afficher le graphique de la première matière lors du démarrage
afficher_premiere_matiere()

root.mainloop()
