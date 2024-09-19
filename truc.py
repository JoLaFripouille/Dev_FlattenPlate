import os
import ezdxf
import pandas as pd
import customtkinter as ctk
from shapely.geometry import Polygon
from tkinter import filedialog, messagebox

# Fonction pour calculer l'aire d'une polyligne fermée dans un fichier DXF
def get_polyline_area(polyline):
    points = [(point[0], point[1]) for point in polyline]
    polygon = Polygon(points)
    if not polygon.is_valid or not polyline.is_closed:
        return None
    area_mm2 = polygon.area
    area_m2 = area_mm2 / 1_000_000
    return round(area_m2, 2)

# Fonction pour traiter les fichiers DXF dans le répertoire sélectionné
def process_dxf_files(directory):
    data = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".dxf"):
            file_path = os.path.join(directory, file_name)
            try:
                doc = ezdxf.readfile(file_path)
                msp = doc.modelspace()
                for entity in msp.query('LWPOLYLINE'):
                    area = get_polyline_area(entity)
                    if area:
                        data.append({
                            "Nom du fichier": os.path.splitext(file_name)[0],
                            "Surface (m²)": area
                        })
            except Exception as e:
                print(f"Erreur avec le fichier {file_name}: {e}")
    
    if data:
        df = pd.DataFrame(data)
        export_to_excel(df)
    else:
        messagebox.showinfo("Résultat", "Aucun fichier DXF valide trouvé ou aucune surface détectée.")

# Fonction pour exporter les résultats dans un fichier Excel
def export_to_excel(df):
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Exportation réussie", f"Les données ont été exportées dans {file_path}")

# Interface graphique avec customtkinter
def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        process_dxf_files(directory)

# Configuration de l'interface graphique
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("400x200")
app.title("Extracteur de Surface DXF")

label = ctk.CTkLabel(app, text="Sélectionnez un répertoire contenant des fichiers DXF")
label.pack(pady=20)

button = ctk.CTkButton(app, text="Sélectionner un répertoire", command=select_directory)
button.pack(pady=20)

app.mainloop()
