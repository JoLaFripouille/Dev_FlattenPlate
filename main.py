import customtkinter as ctk
import json
import tkinter as tk
import numpy as np
import matplotlib
import PIL
import tkinter
import scipy
import os
import ezdxf
import sys
import ctypes
import requests
from PIL import Image
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog, messagebox

# Obtenir le facteur de mise à l'échelle du système (exemple pour Windows)
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
GITHUB_URL = "https://raw.githubusercontent.com/JoLaFripouille/Dev_FlattenPlate/main/data.json"
LOCAL_FILE = "data.json"


def get_resource_path(relative_path):
    """Get the absolute path to a resource in the bundled executable."""
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin des fichiers dedans
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Pour les autres images dans le dossier img
image_path1 = get_resource_path('img\\copyL.png')
image_path2 = get_resource_path('img\\copy.png')
image_path3 = get_resource_path('img\\icon.ico')
image_path4 = get_resource_path('img\\generateDark.png')
image_path5 = get_resource_path('img\\generateLight.png')


matplotlib.use("TkAgg")  # Utilise le backend Tkinter


class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")
        self.title("Calcul de Développé avec Perte au Pli Flatten Plate V1.5")
        self.iconbitmap(image_path3)
        self.geometry("770x670+50+50")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.fermer_fenetre)

        # Chargement des données et initialisation des variables
        self.donnees_materiaux = self.charger_donnees_materiau("data.json")
        self.angles_pli_entries = []
        self.longueur_finale = None

        # Chargement des images
        self.image_copier = ctk.CTkImage(
            light_image=Image.open(image_path2),
            dark_image=Image.open(image_path1),
            size=(24, 24),
        )

        # Chargement des images
        self.image_generate_dxf = ctk.CTkImage(
            light_image=Image.open(image_path5),
            dark_image=Image.open(image_path4),
            size=(90, 110),
        )

        # Configuration de l'interface graphique
        self.setup_gui()

        # Affichage initial du graphique
        self.afficher_premiere_matiere()

    def charger_donnees_materiau(self, nom_fichier):
        with open(nom_fichier, "r") as f:
            return json.load(f)
    
    

    def setup_gui(self):
        # Cadres principaux
        self.frame_principal = ctk.CTkFrame(self, width=450, corner_radius=15)
        self.frame_principal.place(x=350, y=15)

        self.frame_graphique = ctk.CTkFrame(self)
        self.frame_graphique.place(x=15, y=15)

        # Cadre pour la génération de DXF
        self.frame_DXF_height = 295
        self.frame_DXF = ctk.CTkFrame(
            self, width=320, height=self.frame_DXF_height, corner_radius=15
        )
        self.frame_DXF.place_forget()  # Initialement caché

        # Cadre pour le nom de la pièce
        self.frame_DXF_name_height = 58
        self.frame_DXF_name = ctk.CTkFrame(self.frame_DXF, width=320, corner_radius=15)
        self.frame_DXF_name.place(x=10, y=10)

        self.label_name = ctk.CTkLabel(self.frame_DXF_name, text="Nom de pièce :")
        self.label_name.pack(side="left", pady=10, padx=10)
        self.entry_name = ctk.CTkEntry(self.frame_DXF_name, corner_radius=15)
        self.entry_name.pack(pady=10, padx=10)

        # Cadre pour la longueur
        self.frame_DXF_longueur = ctk.CTkFrame(
            self.frame_DXF, width=320, corner_radius=15
        )
        self.frame_DXF_longueur.place(x=10, y=10 + self.frame_DXF_name_height)

        self.label_longueur = ctk.CTkLabel(
            self.frame_DXF_longueur, text="Longueur :       "
        )
        self.label_longueur.pack(side="left", pady=10, padx=10)
        self.entry_longueur = ctk.CTkEntry(self.frame_DXF_longueur, corner_radius=15)
        self.entry_longueur.pack(pady=10, padx=10)

        self.var_bouleen = ctk.BooleanVar()
        self.checkbox_bouleen = ctk.CTkCheckBox(
            self.frame_DXF,
            text="Ajouter des perçages pour suspendre",
            variable=self.var_bouleen,
        )
        self.checkbox_bouleen.place(x=15, y=10 + 30 + 28 + self.frame_DXF_name_height)

        # Cadre pour le chemin du dossier
        self.frame_chemin_dossier = ctk.CTkFrame(
            self.frame_DXF, width=320, height=210, corner_radius=15
        )
        self.frame_chemin_dossier.place(
            x=10, y=10 + 30 + 28 * 2 + 5 + self.frame_DXF_name_height
        )

        self.label_chemin_dossier = ctk.CTkEntry(
            self.frame_chemin_dossier,
            fg_color='transparent',
            justify="center",
            width=285,
            placeholder_text="sélectionnez un dossier de sortie",
            border_width=0
        )
        self.label_chemin_dossier.pack(side="bottom", padx=1, pady=3)

        self.bouton_parcourir = ctk.CTkButton(
            self.frame_chemin_dossier,
            width=200,
            text="Parcourir",
            command=self.ouvrir_dossier,
            corner_radius=15
        )
        self.bouton_parcourir.pack(side="top", padx=48, pady=5)

        # Bouton pour générer le DXF
        self.btn_generate_DXF = ctk.CTkButton(
            self.frame_DXF,
            text="Générer le fichier DXF",
            width=300,
            height=42,
            corner_radius=15,
            border_width=2,
            font=("Dubai", 18),
            command=self.generer,
        )
        self.btn_generate_DXF.place(x=10, y=(self.frame_DXF_height - 42) - 10)

        # Bouton pour afficher le cadre DXF
        self.btn_DXF = ctk.CTkButton(
            self,
            text="",
            fg_color="transparent",
            command=self.launch_generate_DXF,
            image=self.image_generate_dxf,
            width=320,
            height=self.frame_DXF_height,
            corner_radius=20,
            border_width=0,
            font=("Dubai", 25),
        )

        
        # Bouton pour chercher les mises à jour
        self.button_update = ctk.CTkButton(self, text="Chercher mise à jour data", height=32, width=155, corner_radius=16, command=self.check_for_updates)
        self.button_update.place(x=575, y=625)   

        # Cadre pour la sélection du matériau
        self.frame_materiau = ctk.CTkFrame(self.frame_principal)
        self.frame_materiau.pack(pady=10, padx=20)

        self.label_materiau = ctk.CTkLabel(
            self.frame_materiau, text="Sélectionnez la matière:"
        )
        self.label_materiau.grid(row=0, column=0, padx=10, pady=7)

        self.combobox_materiau = ctk.CTkComboBox(
            self.frame_materiau, corner_radius=15, width=180, values=list(self.donnees_materiaux.keys())
        )
        self.combobox_materiau.grid(row=0, column=1, padx=10, pady=5)
        self.combobox_materiau.set(list(self.donnees_materiaux.keys())[0])

        # Cadre pour le nombre de plis
        self.frame_nombre_plis = ctk.CTkFrame(self.frame_principal)
        self.frame_nombre_plis.pack(pady=10, padx=10)

        self.label_nombre_plis = ctk.CTkLabel(
            self.frame_nombre_plis, text="Nombre de plis:"
        )
        self.label_nombre_plis.grid(row=0, column=0, padx=15, pady=7)

        self.entry_nombre_plis_var = tk.StringVar()
        self.entry_nombre_plis_var.trace("w", self.demander_angles)
        self.entry_nombre_plis = ctk.CTkEntry(
            self.frame_nombre_plis, textvariable=self.entry_nombre_plis_var, corner_radius=15
        )
        self.entry_nombre_plis.grid(row=0, column=1, padx=10, pady=7)

        # Cadre pour les angles
        self.frame_angles = ctk.CTkScrollableFrame(self.frame_principal, width=285)
        self.frame_angles.pack(pady=10)

        # Cadre pour la longueur initiale
        self.frame_longueur = ctk.CTkFrame(self.frame_principal, width=350)

        self.label_longueur_initiale = ctk.CTkLabel(
            self.frame_longueur, text="Somme des cotes extérieures:"
        )
        self.label_longueur_initiale.grid(row=0, column=0, padx=10, pady=10)

        self.entry_longueur_initiale = ctk.CTkEntry(self.frame_longueur, corner_radius=15)
        self.entry_longueur_initiale.grid(row=0, column=1, padx=10, pady=10)

        self.btn_calculer = ctk.CTkButton(
            self.frame_longueur, text="Calculer", command=self.calculer_resultat, corner_radius=15
        )
        self.btn_calculer.grid(row=1, column=0, columnspan=2, pady=10)

        # Cadre pour afficher le résultat
        self.frame_resultat = ctk.CTkFrame(
            self.frame_principal,
            border_width=2,
            corner_radius=20,
            border_color="white",
        )

        self.label_resultat = ctk.CTkLabel(
            self.frame_resultat,
            text="",
            font=("Helvetica", 18),
            corner_radius=15,
        )
        self.label_resultat.grid(row=0, column=0, padx=10, pady=5)

        self.btn_copier = ctk.CTkButton(
            self.frame_resultat,
            width=36,
            height=36,
            image=self.image_copier,
            corner_radius=15,
            text="",
            fg_color="transparent",
            command=self.copier_texte_au_presse_papiers,
        )
        self.btn_copier.grid(row=0, column=1, pady=5, padx=9)

    def check_for_updates(self):
        try:
            # Télécharger le fichier depuis GitHub
            response = requests.get(GITHUB_URL)
            response.raise_for_status()  # Vérifie s'il y a des erreurs lors de la requête

            # Charger le contenu distant
            remote_data = response.json()

            # Vérifier si le fichier local existe
            if os.path.exists(LOCAL_FILE):
                with open(LOCAL_FILE, 'r') as local_file:
                    local_data = json.load(local_file)

                # Comparer les deux fichiers
                if local_data == remote_data:
                    self.popup('', "Le fichier est déjà à jour.")
                    
                else:
                    # Mise à jour disponible, changer l'apparence du bouton
                    self.popup('', "Mise à jour disponible !")
                    self.button_update.configure(
                        text="Télécharger mise à jour", 
                        fg_color="yellow", 
                        text_color="black", 
                        border_color="black",
                        hover_color="#c4c22a",
                        border_width=3, 
                        command=self.update_json
                    )
            else:
                # Si le fichier local n'existe pas, il doit être mis à jour
                self.popup('', "Aucune version locale. Mise à jour requise !")
                self.button_update.configure(
                    text="Télécharger mise à jour", 
                    fg_color="yellow", 
                    hover_color="#c4c22a",
                    text_color="black", 
                    border_color="black", 
                    border_width=3, 
                    command=self.update_json
                )

        except Exception as e:
            self.popup('', f"Erreur: {str(e)}")


    def update_json(self):
        try:
            # Télécharger le fichier depuis GitHub
            response = requests.get(GITHUB_URL)
            response.raise_for_status()  # Vérifie s'il y a des erreurs lors de la requête

            # Sauvegarder le fichier localement
            with open(LOCAL_FILE, 'w') as file:
                file.write(response.text)
            self.popup('', f"Mise à jour réussie !")
            self.button_update.configure(
                text="Chercher mise à jour data", 
                fg_color="gray", 
                text_color="white", 
                border_color="black", 
                hover_color="#9c9c9c",
                border_width=0, 
                command=self.check_for_updates
            )

        except Exception as e:
            self.popup('', f"Erreur: {str(e)}")
            

    def run(self):
        self.app.mainloop()

    def launch_generate_DXF(self):
        self.btn_DXF.place_forget()
        self.frame_DXF.place(x=15, y=350)

    def ouvrir_dossier(self):
        dossier = filedialog.askdirectory()
        if dossier:
            self.label_chemin_dossier.delete(0, ctk.END)  # Effacer le contenu existant
            self.label_chemin_dossier.insert(0, dossier)  # Insérer le nouveau chemin

    def generer(self):
        try:
            if self.longueur_finale is None:
                messagebox.showerror(
                    "Erreur",
                    "Veuillez calculer le développé avant de générer le fichier DXF.",
                )
                return

            hauteur = self.longueur_finale
            longueur = float(self.entry_longueur.get())
            bouleen = self.var_bouleen.get()
            chemin_dossier = self.label_chemin_dossier.get()
            nom_fichier = self.entry_name.get()

            if (
                not chemin_dossier
                or chemin_dossier == "Aucun dossier sélectionné"
                or not nom_fichier
            ):
                messagebox.showwarning(
                    "Attention",
                    "Veuillez spécifier le chemin du dossier et le nom du fichier.",
                )
                return

            self.generer_dxf(hauteur, longueur, bouleen, chemin_dossier, nom_fichier)
            self.entry_longueur.delete(0, ctk.END)
            self.entry_name.delete(0, ctk.END)
#largeur
        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Veuillez entrer des valeurs numériques valides pour la longueur.",
            )

    def generer_dxf(self, hauteur, longueur, bouleen, chemin_dossier, nom_fichier):
        # Vérifie que le dossier existe, sinon le crée
        if not os.path.exists(chemin_dossier):
            os.makedirs(chemin_dossier)

        # Vérifie que le nom du fichier se termine par '.dxf'
        if not nom_fichier.lower().endswith(".dxf"):
            nom_fichier += ".dxf"

        # Crée un nouveau document DXF
        doc = ezdxf.new(dxfversion="R2010")
        msp = doc.modelspace()

        # Trace le rectangle
        points = [(0, 0), (longueur, 0), (longueur, hauteur), (0, hauteur), (0, 0)]
        msp.add_lwpolyline(points, close=True)

        # Ajoute les cercles si bouleen est True
        if bouleen:
            rayon = 1.75  # Diamètre 3.5 divisé par 2
            centre_gauche = (5, hauteur - 5)
            centre_droit = (longueur - 5, hauteur - 5)
            msp.add_circle(centre_gauche, rayon)
            msp.add_circle(centre_droit, rayon)

        # Enregistre le fichier DXF
        chemin_complet = os.path.join(chemin_dossier, nom_fichier)
        doc.saveas(chemin_complet)

        self.popup(f"{nom_fichier}", "a été créé avec succès")

    def fermer_fenetre(self):
        self.quit()
        self.destroy()

    def demander_angles(self, *args):
        try:
            nombre_de_plis = int(self.entry_nombre_plis_var.get())

            # Effacer les widgets précédents
            for widget in self.frame_angles.winfo_children():
                widget.destroy()

            self.angles_pli_entries = []  # Entrées pour les angles

            for i in range(nombre_de_plis):
                label_angle = ctk.CTkLabel(
                    self.frame_angles, text=f"Angle du pli {i+1}:"
                )
                label_angle.grid(row=i, column=0, padx=10, pady=10)

                entry_angle = ctk.CTkEntry(self.frame_angles, corner_radius=15)
                entry_angle.grid(row=i, column=1, padx=10, pady=10)
                self.angles_pli_entries.append(entry_angle)

            self.frame_longueur.pack(pady=10, padx=10)

        except ValueError:
            pass  # Ignore si ce n'est pas un entier valide

    def popup(self, valeur, suffixe):
        frame_popup = ctk.CTkFrame(
            self,
            width=250,
            height=30,
            corner_radius=0,
            border_width=4,
            border_color="white",
        )
        label_popup = ctk.CTkLabel(
            frame_popup,
            height=20,
            text=f'{valeur}  {suffixe}',
            font=("Dubai", 16),
        )
        label_popup.pack(pady=5, padx=20)

        def entrer_par_le_haut(y=0):
            if y <= 10:
                frame_popup.place(x=10, y=y)
                self.after(10, entrer_par_le_haut, y + 1)
            else:
                self.after(2000, glisser_vers_la_gauche)

        def glisser_vers_la_gauche(x=10):
            if x >= -210:
                frame_popup.place(x=x, y=10)
                self.after(10, glisser_vers_la_gauche, x - 6)
            else:
                frame_popup.destroy()

        entrer_par_le_haut()

    def copier_texte_au_presse_papiers(self):
        if self.longueur_finale is not None:
            self.clipboard_clear()
            valeur = self.longueur_finale
            self.clipboard_append(f"{valeur:.2f}")
            self.popup(f"{valeur:.2f}", "copié dans le presse-papiers")
        else:
            messagebox.showwarning("Attention", "Aucune valeur à copier.")

    def calculer_resultat(self):
        try:
            materiau = self.combobox_materiau.get()
            angles = np.array(self.donnees_materiaux[materiau]["angles"])
            developes = np.array(self.donnees_materiaux[materiau]["developes"])

            pertes = 100 - developes  # Perte = 100 - Développement

            angles_sorted = np.sort(angles)
            pertes_sorted = pertes[np.argsort(angles)]

            spline = CubicSpline(angles_sorted, pertes_sorted)

            angles_values = [float(entry.get()) for entry in self.angles_pli_entries]
            expression = self.entry_longueur_initiale.get()
            result = eval(expression)
            longueur_initiale = float(result)

            perte_totale = sum(spline(angle) for angle in angles_values)
            self.longueur_finale = longueur_initiale - perte_totale

            self.label_resultat.configure(
                text=f"Développé :  {self.longueur_finale:.2f} mm"
            )

            angle_fit = np.linspace(min(angles_sorted), max(angles_sorted), 500)
            perte_spline = spline(angle_fit)

            pertes_values = spline(angles_values)

            self.btn_DXF.place(x=15, y=350)
            self.frame_resultat.pack(pady=10, padx=10)

            self.afficher_graphique(
                angles_sorted,
                pertes_sorted,
                angle_fit,
                perte_spline,
                angles_values,
                pertes_values,
            )
        except Exception as e:
            messagebox.showerror(
                "Erreur", f"Erreur: '{str(e)}' remplissez correctement les champs"
            )

    def afficher_graphique(
        self,
        angles_sorted,
        pertes_sorted,
        angle_fit,
        perte_spline,
        angles_values,
        pertes_values,
    ):
        scale_factor = user32.GetDpiForWindow(self.frame_graphique.winfo_id()) / 96
        # Définir la taille du graphique en pixels (par exemple 600x400 pixels) et un DPI de 100
        width_pixels = 320
        height_pixels = 320
        base_dpi = 100
        dpi = base_dpi * scale_factor  # Ajuster le DPI en fonction de la mise à l'échelle
        
        # Convertir la taille en pouces
        fig_width_inch = width_pixels / dpi
        fig_height_inch = height_pixels / dpi

        # Créer la figure avec la taille en pouces et le DPI spécifié
        fig, ax = plt.subplots(figsize=(fig_width_inch, fig_height_inch), dpi=dpi)

        ax.scatter(
            angles_sorted, pertes_sorted, color="blue", label="Perte au pli (bleu)"
        )

        ax.plot(angle_fit, perte_spline, color="green", label="Spline cubique (perte)")

        ax.scatter(
            angles_values,
            pertes_values,
            color="red",
            label="Points saisis (rouge)",
            zorder=5
        )

        ax.set_xlabel("Angle (degrés)", fontsize=5)
        ax.set_ylabel("Perte au pli (mm)", fontsize=5)
        ax.set_title("Perte au pliage en fonction de l'angle", fontsize=6)
        ax.tick_params(axis='both', which='major', labelsize=4)  # Taille réduite pour les ticks
        ax.grid(True)
        ax.legend(fontsize=5)

        for widget in self.frame_graphique.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_graphique)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def afficher_premiere_matiere(self):
        premiere_matiere = self.combobox_materiau.get()
        angles = np.array(self.donnees_materiaux[premiere_matiere]["angles"])
        developes = np.array(self.donnees_materiaux[premiere_matiere]["developes"])

        pertes = 100 - developes
#longueur
        angles_sorted = np.sort(angles)
        pertes_sorted = pertes[np.argsort(angles)]

        spline = CubicSpline(angles_sorted, pertes_sorted)

        angle_fit = np.linspace(min(angles_sorted), max(angles_sorted), 500)
        perte_spline = spline(angle_fit)

        self.afficher_graphique(
            angles_sorted, pertes_sorted, angle_fit, perte_spline, [], []
        )


if __name__ == "__main__":
    app = Application()
    app.mainloop()
