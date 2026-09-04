# sprezzature-colors

Outils d'accessibilité des couleurs et d'export de palette pour la suite [sprezzature](https://harchaoui.org/warith/sprezzature/).

## Le problème que ça résout

Prenons un bouton avec un texte gris clair sur fond blanc. Pour la plupart des gens, il se lit sans effort. Pour une personne malvoyante, ou en plein soleil sur l'écran d'un téléphone, le même bouton peut devenir illisible : le texte et le fond sont trop proches en luminosité pour que l'œil les sépare. Le même écart apparaît quand un graphique utilise le rouge pour « en baisse » et le vert pour « en hausse » : environ un homme sur douze présente une forme de déficience de la vision des couleurs (le fait de ne pas distinguer certaines teintes, le plus souvent le rouge du vert) et voit les deux barres de la même couleur.

Ce paquet fournit trois outils déterministes, qui ne dépendent que de la bibliothèque standard, pour repérer ces écarts avant qu'une maquette ne parte en production, plutôt que de compter sur le hasard d'une remarque :

- **Audit de contraste.** Vérifie chaque paire (texte, fond) d'une palette par rapport aux seuils publiés par les Règles pour l'accessibilité des contenus web (*Web Content Accessibility Guidelines* ou WCAG, le corpus de règles de référence pour rendre un contenu web utilisable par des personnes en situation de handicap), et propose une correction qui reste visuellement proche de la couleur d'origine.
- **Simulation de daltonisme.** Génère l'image telle que la verrait une personne atteinte de protanopie, deutéranopie ou tritanopie (les trois formes courantes de daltonisme, respectivement liées au rouge, au vert et au bleu), pour vérifier une maquette avant sa mise en ligne plutôt qu'après une plainte.
- **Export de palette Tailwind.** Écrit les couleurs de marque validées du projet sous forme d'un bloc de configuration Tailwind CSS prêt à l'emploi, pour que chaque projet de la suite parte de la même source plutôt que de recopier des codes hexadécimaux à la main.

Les trois outils fonctionnent avec la seule bibliothèque standard (la simulation de daltonisme a en plus besoin de Pillow, une bibliothèque Python de traitement d'image, pour lire et écrire les fichiers image). Rien ici n'appelle le réseau ni un modèle d'intelligence artificielle.

---

## Installation

```bash
pip install sprezzature-colors
```

Pour la simulation de daltonisme sur des images :

```bash
pip install sprezzature-colors[cvd]
```

`pip install` ajoute aussi quatre commandes au PATH :
`sprezzature-colors-contrast`, `sprezzature-colors-cvd`,
`sprezzature-colors-palette-to-tailwind` et `sprezzature-colors-levels`.
Les exemples ci-dessous utilisent la forme `python scripts/….py`, celle
d'un dépôt cloné (`git clone` puis `pip install -e ".[dev,cvd]"`) ; après
un `pip install` classique, utilisez plutôt la commande correspondante,
par exemple `sprezzature-colors-contrast --fix` au lieu de
`python scripts/audit_contrast.py --fix`.

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

Le « ratio » ici est le ratio de contraste WCAG : un nombre allant de 1 (luminosités identiques, illisible) à 21 (noir pur sur blanc pur). 4,5 est le seuil WCAG pour le texte courant.

Avec une palette JSON externe :

```bash
python scripts/audit_contrast.py --palette ma-palette.json --target 7 --fix
python scripts/audit_contrast.py --palette ma-palette.json --format json
```

### Simulation de daltonisme

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

### Niveaux d'accessibilité

```bash
# Prévisualiser la palette canonique au niveau fort contraste (AAA)
python scripts/accessibility_levels.py --level high-contrast

# Niveaux disponibles : universal (défaut), high-contrast, monochrome,
#                       deuteranopia, protanopia, tritanopia
```

---

## Utilisation en bibliothèque

```python
from scripts._colors import contrast_ratio_hex, meets_wcag, lighten, darken, simulate_pixel, CVD_MATRICES

# Ratio de contraste WCAG
ratio = contrast_ratio_hex("#007AFF", "#FFFFFF")   # -> 4.55

# Test WCAG AA
ok = meets_wcag("#007AFF", "#FFFFFF", level="AA", size="normal")   # -> True

# Éclaircir / assombrir de façon perceptuelle (axe OKLCH, teinte conservée) :
# OKLCH est un modèle de couleur construit pour qu'un même pas numérique de
# luminosité corresponde à un même écart de clarté perçu par l'œil, ce que
# le RGB brut ne garantit pas (le même pas numérique peut y paraître à peine
# visible dans une zone et brutal dans une autre).
plus_clair = lighten("#007AFF", 0.15)   # -> "#5FA8FF" (approx.)
plus_sombre = darken("#007AFF", 0.10)   # -> "#005DC2" (approx.)

# Simulation de daltonisme pixel par pixel
r, g, b = simulate_pixel((255, 0, 0), CVD_MATRICES["protanopia"])
```

---

## Fonctionnalités

| Fonctionnalité | Détail |
|---|---|
| Audit de contraste WCAG | AA (4,5:1), AA grand texte (3:1), AAA (7:1) |
| Composition alpha | Premiers plans translucides `#RRGGBBAA` composités avant le calcul du ratio |
| Suggestions de correction | Voisin OKLCH le plus proche qui franchit le seuil |
| Simulation de daltonisme | Matrices de Machado et al. 2009 (protanopie, deutéranopie, tritanopie) |
| Vérification en niveaux de gris | Luminance relative, pour détecter les distinctions qui reposent sur la teinte seule |
| Export palette Tailwind | Bloc `theme.extend.colors` ou configuration `module.exports` complète |
| Niveaux d'accessibilité | universel / fort contraste / monochrome / palette adaptée à une déficience précise |
| Dépendances | Bibliothèque standard uniquement, plus Pillow pour le rendu de la simulation |

---

## Sciences des couleurs

Les ratios de contraste suivent la norme WCAG 2.x : la luminance relative (à quel point une couleur paraît claire à l'œil, pas seulement ses valeurs RGB brutes) utilise la fonction de transfert gamma 2,4 que fixe la norme. Les ajustements perceptuels utilisent OKLab et OKLCH, un modèle de couleur conçu par Björn Ottosson (2020) précisément pour qu'un même pas numérique de luminosité corresponde au même écart de clarté perçu par l'œil, ce que le RGB brut ne garantit pas. Les matrices de simulation du daltonisme viennent de Machado, Oliveira et Fernandes (2009, revue *IEEE Transactions on Visualization and Computer Graphics*), un article largement cité qui a mesuré comment chaque type de daltonisme transforme une couleur perçue et a publié cette transformation sous forme d'une matrice de nombres, exactement ce que stocke `CVD_MATRICES`.

---

## Partie de la suite sprezzature

| Dépôt | Fonction |
|---|---|
| [sprezzature](https://github.com/warith-harchaoui/sprezzature) | Neuf compétences + site web |
| [sprezzature-colors](https://github.com/warith-harchaoui/sprezzature-colors) | Ce dépôt |
| [sprezzature-figures](https://github.com/warith-harchaoui/sprezzature-figures) | Visualisation de données |
| [best-engine-ai-helper](https://github.com/warith-harchaoui/best-engine-ai-helper) | Runtime LLM/VLM hors ligne |

---

## Auteur

Warith Harchaoui, [harchaoui.org/warith](https://harchaoui.org/warith)

Licence : BSD-3-Clause
