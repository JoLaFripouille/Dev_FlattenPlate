import re
import pdfplumber

# Ouvrir le fichier PDF
with pdfplumber.open(r"C:/Users/Salon/Downloads/FPS6 - FER SUP PC - Rev A.pdf") as pdf:
    # Sélectionner la première page (ou la page désirée)
    page = pdf.pages[0]

    # Définir les coordonnées pour la zone
    crop_box = (1100, 900, 1600, 1180)  # Ajustez ces valeurs en fonction de la zone
    cropped_page = page.within_bbox(crop_box)
    text = cropped_page.extract_text()

    # Afficher le texte extrait pour vérification
    print("Texte extrait de la zone définie :")
    print(text)

    # Rechercher le repère ("FPS6")
    repere = re.search(r'(FPS6)', text)
    
    # Rechercher la quantité (nombre après le repère)
    quantite = re.search(r'FPS6\s+(\d+)', text)
    
    # Rechercher la longueur (nombre après "PL2*196")
    longueur = re.search(r'PL2\*196\s+(\d+)', text)

    # Afficher les données extraites
    if repere:
        print(f"Repère: {repere.group(1)}")
    else:
        print("Repère non trouvé")
    
    if quantite:
        print(f"Quantité: {quantite.group(1)}")
    else:
        print("Quantité non trouvée")
    
    if longueur:
        print(f"Longueur: {longueur.group(1)}")
    else:
        print("Longueur non trouvée")
