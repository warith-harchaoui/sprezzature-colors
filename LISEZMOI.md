# sprezzature-colors

Outils d'accessibilité des couleurs et d'export de palette pour la suite [sprezzature](https://harchaoui.org/warith/sprezzature/).

Trois outils en un seul paquet :

- **Audit de contraste WCAG** -- vérifie chaque paire (premier plan, arrière-plan) par rapport aux seuils 4,5:1, 3:1 et 7:1. Propose des corrections qui restent sur la même teinte.
- **Simulation de déficience chromatique** -- génère des versions d'une image telles qu'elles apparaissent aux personnes atteintes de protanopie, deutéranopie ou tritanopie. Produit des fichiers séparés ou une mosaïque 2x2 pour la revue de design.
- **Export palette Tailwind CSS** -- écrit la palette de marque canonique sous forme d'un bloc `tailwind.config.js` ou d'une configuration complète, avec variantes sombres dérivées en option.

Tous les scripts sont déterministes et fonctionnent avec la bibliothèque standard (la simulation CVD nécessite Pillow). Aucun accès réseau à l'import.

---

## Installation

```bash
pip install sprezzature-colors
```

Pour la simulation CVD sur des images :

```bash
pip install sprezzature-colors[cvd]
```

---

## Démarrage rapide

### Audit de contraste

```bash
python scripts/audit_contrast.py
# Target ratio: 4.5
#
#   ✓      brand-blue  on  surface-primary    ratio 4.55
#   ✗      brand-red   on  surface-secondary  ratio 2.83
#       -> suggest #D4000A  (ratio 4.51)
```

Avec une palette JSON externe :

```bash
python scripts/audit_contrast.py --palette ma-palette.json --target 7 --fix
python scripts/audit_contrast.py --palette ma-palette.json --format json
```

### Simulation de déficience chromatique

```bash
# Trois fichiers PNG frères
python scripts/simulate_cvd.py hero.png

# Mosaïque 2x2 pour la revue de design
python scripts/simulate_cvd.py hero.png --grid --out hero-cvd-grille.png

# Deutéranopie seulement + niveau de gris
python scripts/simulate_cvd.py hero.png --types deut --grayscale
```

### Palette vers Tailwind

```bash
# Bloc à coller dans une configuration existante
python scripts/palette_to_tailwind.py

# tailwind.config.js complet avec variantes sombres dérivées
python scripts/palette_to_tailwind.py --emit config --with-dark --out tailwind.config.js
```

---

## Fonctionnalités

| Fonctionnalité | Détail |
|---|---|
| Audit de contraste WCAG | AA (4,5:1), AA-large (3:1), AAA (7:1) |
| Composition alpha | Premiers plans translucides `#RRGGBBAA` composités avant le ratio |
| Suggestions de correction | Voisin OKLCH le plus proche qui passe le seuil |
| Simulation CVD | Matrices Machado et al. 2009 (protanopie, deutéranopie, tritanopie) |
| Vérification en niveaux de gris | Luminance relative pour détecter les distinctions basées sur la teinte seule |
| Export palette Tailwind | Bloc `theme.extend.colors` ou config `module.exports` complète |
| Niveaux d'accessibilité | universel / fort contraste / monochrome / remappage CVD spécifique |
| Dépendances | Bibliothèque standard uniquement (+ Pillow pour le rendu CVD) |

---

## Sciences des couleurs

Les ratios de contraste suivent WCAG 2.x : la luminance relative utilise la fonction de transfert gamma 2,4. Les ajustements perceptuels utilisent OKLab / OKLCH (Bjorn Ottosson, 2020). Les matrices CVD sont issues de Machado, Oliveira, Fernandes (2009), IEEE TVCG.

---

## Partie de la suite sprezzature

| Dépôt | Fonction |
|---|---|
| [sprezzature](https://github.com/warith-harchaoui/sprezzature) | Neuf compétences + site web |
| [sprezzature-colors](https://github.com/warith-harchaoui/sprezzature-colors) | Ce dépôt |
| [sprezzature-figures](https://github.com/warith-harchaoui/sprezzature-figures) | Visualisation de données |
| [sprezzature-local](https://github.com/warith-harchaoui/sprezzature-local) | Runtime LLM hors ligne |

---

## Auteur

Warith Harchaoui -- [harchaoui.org/warith](https://harchaoui.org/warith)

Licence : BSD-3-Clause
