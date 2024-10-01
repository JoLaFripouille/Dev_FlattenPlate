import re

# Texte extrait des deux lignes
line1 = "FPS6 1 Habillage PL2*196 1127 S235JR Laqué autreIntru"
line2 = "intrus Repère Qté Nom Profil Longueur Qualité Finition"

# Définir les types de données attendus pour chaque label
expected_types = {
    "Repère": str,
    "Qté": int,
    "Nom": str,
    "Profil": str,
    "Longueur": float,
    "Qualité": str,
    "Finition": str
}

# Diviser les lignes en tokens
tokens_line1 = line1.split()
labels_line2 = line2.split()

# Supprimer les intrus connus de labels_line2 (par exemple, "N")
labels_line2 = [label for label in labels_line2 if label in expected_types]

# Fonction pour vérifier si un token correspond au type attendu
def matches_type(token, expected_type):
    if expected_type == int:
        return token.isdigit()
    elif expected_type == float:
        return re.match(r'^\d+(\.\d+)?$', token) is not None
    elif expected_type == str:
        return True  # Tout token est acceptable en tant que chaîne
    else:
        return False

# Fonction pour tenter différents alignements et compter les correspondances
def attempt_alignment(tokens, labels):
    max_matches = -1
    best_alignment = None

    max_shift = len(tokens) - len(labels)
    for shift in range(-len(labels), len(tokens)):
        matches = 0
        alignment = []
        for i, label in enumerate(labels):
            token_index = i + shift
            if 0 <= token_index < len(tokens):
                token = tokens[token_index]
                expected_type = expected_types[label]
                if matches_type(token, expected_type):
                    matches += 1
                alignment.append((label, token))
            else:
                alignment.append((label, None))  # Aucun token à associer
        if matches > max_matches:
            max_matches = matches
            best_alignment = alignment

    return best_alignment

# Tenter d'aligner les tokens avec les labels
alignment = attempt_alignment(tokens_line1, labels_line2)

# Afficher l'alignement
print("Alignement :")
for label, token in alignment:
    print(f"{label}: {token}")

# Construire un dictionnaire des données extraites
extracted_data = {}
for label, token in alignment:
    if token is not None:
        extracted_data[label] = token

# Afficher les valeurs extraites
print("\nDonnées extraites :")
for label, value in extracted_data.items():
    print(f"{label}: {value}")
