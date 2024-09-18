import customtkinter as ctk
import json
import numpy as np
from scipy.interpolate import UnivariateSpline

# Charger les données des matériaux
def charger_donnees_materiau(nom_fichier):
    with open(nom_fichier, 'r') as f:
        return json.load(f)

# Calculer la longueur finale
def calculer_longueur_finale(longueur_initiale, angles_pli, spline_perte):
    perte_totale = sum(spline_perte(angle) for angle in angles_pli)
    longueur_finale = longueur_initiale - perte_totale
    return longueur_finale

# Fonction pour mettre à jour l'interface avec les champs pour les angles
def demander_angles():
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
    
    frame_longueur.pack(pady=10)

# Fonction pour calculer et afficher le résultat
def calculer_resultat():
    try:
        materiau = combobox_materiau.get()
        angles = np.array(donnees_materiaux[materiau]["angles"])
        developes = np.array(donnees_materiaux[materiau]["developes"])

        perte_pli = 100 - developes
        sorted_indices = np.argsort(angles)
        angles_sorted = angles[sorted_indices]
        perte_pli_sorted = perte_pli[sorted_indices]

        spline_perte = UnivariateSpline(angles_sorted, perte_pli_sorted, s=0)
        
        # Récupérer les valeurs d'angles saisies
        angles_values = [float(entry.get()) for entry in angles_pli]
        longueur_initiale = float(entry_longueur_initiale.get())
        
        longueur_finale = calculer_longueur_finale(longueur_initiale, angles_values, spline_perte)
        label_resultat.configure(text=f"Longueur finale: {longueur_finale:.2f}")
    except Exception as e:
        label_resultat.configure(text=f"Erreur: {str(e)}")

# Chargement des données des matériaux
donnees_materiaux = charger_donnees_materiau("data.json")
angles_pli = []

# Initialisation de la fenêtre principale
root = ctk.CTk()
root.title("Calcul de Pliage")
root.geometry("500x600")

# Frame pour la sélection du matériau
frame_materiau = ctk.CTkFrame(root)
frame_materiau.pack(pady=10)

label_materiau = ctk.CTkLabel(frame_materiau, text="Sélectionnez la matière:")
label_materiau.grid(row=0, column=0, padx=10, pady=5)

combobox_materiau = ctk.CTkComboBox(frame_materiau, values=list(donnees_materiaux.keys()))
combobox_materiau.grid(row=0, column=1, padx=10, pady=5)

# Frame pour entrer le nombre de plis
frame_nombre_plis = ctk.CTkFrame(root)
frame_nombre_plis.pack(pady=10)

label_nombre_plis = ctk.CTkLabel(frame_nombre_plis, text="Nombre de plis:")
label_nombre_plis.grid(row=0, column=0, padx=10, pady=5)

entry_nombre_plis = ctk.CTkEntry(frame_nombre_plis)
entry_nombre_plis.grid(row=0, column=1, padx=10, pady=5)

btn_valider_nombre_plis = ctk.CTkButton(frame_nombre_plis, text="Entrer", command=demander_angles)
btn_valider_nombre_plis.grid(row=1, column=0, columnspan=2, pady=10)

# Frame pour entrer les angles de chaque pli
frame_angles = ctk.CTkFrame(root)
frame_angles.pack(pady=10)

# Frame pour entrer la longueur initiale
frame_longueur = ctk.CTkFrame(root)

label_longueur_initiale = ctk.CTkLabel(frame_longueur, text="Longueur initiale:")
label_longueur_initiale.grid(row=0, column=0, padx=10, pady=5)

entry_longueur_initiale = ctk.CTkEntry(frame_longueur)
entry_longueur_initiale.grid(row=0, column=1, padx=10, pady=5)

btn_calculer = ctk.CTkButton(frame_longueur, text="Calculer", command=calculer_resultat)
btn_calculer.grid(row=1, column=0, columnspan=2, pady=10)

# Frame pour afficher le résultat
frame_resultat = ctk.CTkFrame(root)
frame_resultat.pack(pady=10)

label_resultat = ctk.CTkLabel(frame_resultat, text="")
label_resultat.pack()

root.mainloop()
