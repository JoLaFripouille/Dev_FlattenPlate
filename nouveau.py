import customtkinter
import os
import ezdxf
from tkinter import filedialog, messagebox

def generer_dxf(hauteur, largeur, bouleen, chemin_dossier, nom_fichier):
    """
    Génère un fichier DXF contenant un rectangle de dimensions spécifiées.
    Optionnellement, ajoute deux cercles de diamètre 3.5 aux coins supérieurs
    gauche et droit du rectangle, à une distance de 5 unités des bords.
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

    messagebox.showinfo("Succès", f"Fichier DXF généré avec succès à l'emplacement:\n{chemin_complet}")

def ouvrir_dossier():
    dossier = filedialog.askdirectory()
    if dossier:
        entry_chemin_dossier.delete(0, customtkinter.END)
        entry_chemin_dossier.insert(0, dossier)

def generer():
    try:
        hauteur = float(entry_hauteur.get())
        largeur = float(entry_largeur.get())
        bouleen = var_bouleen.get()
        chemin_dossier = entry_chemin_dossier.get()
        nom_fichier = entry_nom_fichier.get()

        if not chemin_dossier or not nom_fichier:
            messagebox.showwarning("Attention", "Veuillez spécifier le chemin du dossier et le nom du fichier.")
            return

        generer_dxf(hauteur, largeur, bouleen, chemin_dossier, nom_fichier)
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides pour la hauteur et la largeur.")

# Configuration de l'interface graphique
customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

app = customtkinter.CTk()
app.title("Générateur de DXF")
app.geometry("500x400")

# Champs de saisie et étiquettes
label_hauteur = customtkinter.CTkLabel(app, text="Hauteur:")
label_hauteur.pack(pady=(20, 0))
entry_hauteur = customtkinter.CTkEntry(app)
entry_hauteur.pack(pady=5)

label_largeur = customtkinter.CTkLabel(app, text="Largeur:")
label_largeur.pack(pady=(20, 0))
entry_largeur = customtkinter.CTkEntry(app)
entry_largeur.pack(pady=5)

var_bouleen = customtkinter.BooleanVar()
checkbox_bouleen = customtkinter.CTkCheckBox(app, text="Ajouter les cercles", variable=var_bouleen)
checkbox_bouleen.pack(pady=(20, 0))

label_chemin_dossier = customtkinter.CTkLabel(app, text="Chemin du dossier:")
label_chemin_dossier.pack(pady=(20, 0))
frame_chemin_dossier = customtkinter.CTkFrame(app)
frame_chemin_dossier.pack(pady=5, padx=10, fill="x")

entry_chemin_dossier = customtkinter.CTkEntry(frame_chemin_dossier)
entry_chemin_dossier.pack(side="left", fill="x", expand=True)
bouton_parcourir = customtkinter.CTkButton(frame_chemin_dossier, text="Parcourir", command=ouvrir_dossier)
bouton_parcourir.pack(side="right", padx=5)

label_nom_fichier = customtkinter.CTkLabel(app, text="Nom du fichier:")
label_nom_fichier.pack(pady=(20, 0))
entry_nom_fichier = customtkinter.CTkEntry(app)
entry_nom_fichier.pack(pady=5)

# Bouton pour générer le DXF
bouton_generer = customtkinter.CTkButton(app, text="Générer le DXF", command=generer)
bouton_generer.pack(pady=30)

app.mainloop()
