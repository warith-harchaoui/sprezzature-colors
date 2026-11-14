# sprezzature-colors

Outils d'accessibilité des couleurs et d'export de palette pour la suite [sprezzature](https://sprezzature.ai/) : le contraste mesuré selon les WCAG (*Web Content Accessibility Guidelines*, la norme internationale qui dit par exemple à quel point un texte doit trancher sur son fond), les couleurs ajustées en OKLCH (*OK Lightness Chroma Hue*, un modèle de couleur où éclaircir de 0,1 se voit autant quelle que soit la teinte).

## Comment ça marche

![Schéma de flux. En haut, une palette ou une image alimente deux voies. La voie de gauche contrôle : elle compose les couleurs translucides, mesure le rapport de contraste WCAG de chaque paire, et simule les trois déficiences de la vision des couleurs, puis rend un verdict par paire. La voie de droite fabrique : elle fige la teinte et la saturation, parcourt l'axe de clarté OKLCH, et nivelle toute la palette, puis rend la couleur conforme la plus proche et une configuration Tailwind. Les deux se rejoignent en un seul résultat, une palette qui survit à un écran bon marché, au plein soleil et à une imprimante en noir et blanc.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-colors/main/assets/comment-ca-marche.svg)

## Le problème que ça résout

Prenons un bouton avec un texte gris clair sur fond blanc. Pour la plupart des gens, il se lit sans effort. Pour une personne malvoyante, ou en plein soleil sur l'écran d'un téléphone, le même bouton peut devenir illisible : le texte et le fond sont trop proches en luminosité pour que l'œil les sépare. Le même écart apparaît quand un graphique utilise le rouge pour « en baisse » et le vert pour « en hausse » : environ un homme sur douze présente une forme de déficience de la vision des couleurs (le fait de ne pas distinguer certaines teintes, le plus souvent le rouge du vert) et voit les deux barres de la même couleur.

Ce paquet fournit quatre outils déterministes pour repérer ces écarts avant qu'une maquette ne parte en production, plutôt que de compter sur le hasard d'une remarque :

- **Audit de contraste.** Vérifie les paires (texte, fond) d'une palette par rapport aux seuils des Règles pour l'accessibilité des contenus web (*Web Content Accessibility Guidelines* ou WCAG, le corpus de règles de référence pour rendre un contenu web utilisable par des personnes en situation de handicap), et propose une correction qui reste visuellement proche de la couleur d'origine.
- **Simulation de daltonisme.** Génère l'image telle que la verrait une personne atteinte de protanopie, deutéranopie ou tritanopie (les trois formes de daltonisme, respectivement liées au rouge, au vert et au bleu), avec en option une version en niveaux de gris.
- **Niveaux d'accessibilité.** Transpose la palette maison vers l'un de six niveaux (universel, fort contraste, monochrome, et un par déficience) en gardant le nom de chaque couleur.
- **Export de palette Tailwind.** Écrit les couleurs de marque validées du projet sous forme d'un bloc de configuration prêt à l'emploi pour Tailwind CSS (*Cascading Style Sheets*, les règles qui fixent couleurs, polices et marges d'une page web, comme « tous les titres en bleu »), pour que chaque projet de la suite parte de la même source plutôt que de recopier des codes hexadécimaux à la main.

Le calcul des couleurs est écrit sur la seule bibliothèque standard de Python. Pillow, une bibliothèque Python de traitement d'image, lit et écrit les fichiers image de la simulation. Rien ici n'appelle le réseau ni un modèle d'intelligence artificielle.

---

## Installation

```bash
pip install sprezzature-colors
```

Cette seule ligne installe tout : les quatre outils, la ligne de commande (click), la simulation sur image (Pillow), l'API (*Application Programming Interface*, des adresses web auxquelles un autre programme envoie une requête et dont il reçoit une réponse) HTTP (*HyperText Transfer Protocol*, l'échange question-réponse qu'un navigateur fait pour chaque page qu'il charge), servie par FastAPI et uvicorn, et le serveur MCP (Model Context Protocol, le protocole par lequel les agents IA appellent des outils en français), servi par fastapi-mcp. Il n'y a aucun extra de fonctionnalité. Le seul extra est `[dev]`, la chaîne de test (pytest, ruff, mypy), pour un dépôt cloné :

```bash
git clone https://github.com/warith-harchaoui/sprezzature-colors
cd sprezzature-colors
pip install -e ".[dev]"
```

## Cinq surfaces

| Surface | Point d'entrée |
|---|---|
| Bibliothèque | `import sprezzature_colors as sc` |
| Ligne de commande | `sprezzature-colors` (aussi `make-colors`), et une commande par outil |
| API HTTP | `uvicorn sprezzature_colors.api:app`, ou `docker compose up` (qui sert aussi le point d'accès MCP) |
| Serveur MCP | `sprezzature-colors-mcp` |
| Skill | `sprezzature_colors/skill/` (`SKILL.md` et ses références), livré dans le paquet ; `sprezzature-colors-skill --install` le range là où l'agent le lit |

La cinquième surface est le skill : le dossier qu'un agent comme Claude Code ou OpenCode lit pour savoir quand prendre ces outils et quelle commande lancer. Il voyage dans la roue, si bien que `pip install` apporte les cinq surfaces. [TRIGGERS.md](https://github.com/warith-harchaoui/sprezzature-colors/blob/main/TRIGGERS.md) dit quel outil répond à quelle demande, sur chaque surface.

---

## Ligne de commande

### Une porte d'entrée, deux orthographes, quatre outils

```bash
sprezzature-colors --help             # les quatre outils, et ce que fait chacun
sprezzature-colors tools              # quels outils tournent sur cette machine
sprezzature-colors contrast --fix     # lancer un outil par la porte d'entrée
make-colors contrast --fix            # la même commande, sous le nom historique
sprezzature-colors skill              # le skill installé est-il à jour avec ce paquet ?
```

`make-colors` et `sprezzature-colors` désignent le même groupe click, donc ils ne peuvent pas diverger. Ses sous-commandes sont `contrast`, `cvd`, `levels`, `palette-to-tailwind`, `tools` et `skill`. Le groupe répond à `-V` / `--version`, et affiche à la fin de `--help` les lignes de complétion pour bash et zsh.

Chaque outil est aussi sa propre commande, et c'est ce qu'un script ou un crochet de pré-commit devrait appeler :

| Commande | Outil |
|---|---|
| `sprezzature-colors-contrast` | Audit de contraste WCAG d'une palette |
| `sprezzature-colors-cvd` | Simulation de daltonisme sur une image |
| `sprezzature-colors-levels` | Palette transposée vers un niveau d'accessibilité |
| `sprezzature-colors-palette-to-tailwind` | Palette exportée en configuration Tailwind |

Ces quatre commandes lisent leurs propres options ; la porte d'entrée leur transmet tels quels tous les arguments qui suivent le nom de la sous-commande. Depuis un dépôt cloné, les mêmes outils s'écrivent `python scripts/audit_contrast.py --fix`, un fichier par commande.

### Le skill

```bash
sprezzature-colors-skill                         # rapport : la copie installée est-elle à jour ?
sprezzature-colors-skill --install               # la copier dans ~/.claude/skills/sprezzature-colors
sprezzature-colors-skill --install --agent opencode   # dans ~/.opencode/skills à la place
sprezzature-colors-skill --path                  # où pip l'a rangé
```

`sprezzature-colors skill` est la même commande par la porte d'entrée. Par défaut elle ne fait que rendre compte, et sort en 0 que les copies diffèrent ou non. `--install` écrit sous votre dossier personnel ; une copie précédente est déplacée dans `~/.claude/skills-superseded/`, hors du dossier des skills, pour que l'agent ne la lise pas comme un second skill. Depuis Python, `sprezzature_colors.skill_path()` renvoie le dossier.

---

## Démarrage rapide

### Audit de contraste

```bash
sprezzature-colors-contrast --fix
# Target ratio: 4.5
#
#   ✗             brand-blue  on         surface-primary   ratio 3.52
#       → suggest #0071E6  (ratio 4.66)
#   ✓             brand-blue  on    surface-primary-dark   ratio 5.97
#   ...
# 35 pass, 21 fail.
```

Le « ratio » ici est le ratio de contraste WCAG : un nombre allant de 1 (luminosités identiques, illisible) à 21 (noir pur sur blanc pur). 4,5 est le seuil WCAG pour le texte courant. Sans `--palette`, l'audit lit sa palette par défaut intégrée. Le code de sortie vaut 0 quand toutes les paires vérifiées passent, 1 quand une paire échoue, et 2 quand rien n'a pu être vérifié : aucune paire dans la palette, ou une palette illisible.

Par défaut, seules les paires qui peuvent se rencontrer dans un thème rendu sont vérifiées : textes clairs sur surfaces claires, textes sombres sur surfaces sombres, accents de marque sur toutes les surfaces. `--all-pairs` vérifie le produit croisé complet. Les rôles sont reconnus par préfixe : `label-` et `brand-` sont des premiers plans (sauf les teintes `-light`), `surface-` est un fond, et toute autre clé est ignorée.

Avec une palette externe en JSON (*JavaScript Object Notation*, un format texte où les programmes rangent des données en champs nommés, comme {"nom": "Ada"}) :

```bash
sprezzature-colors-contrast --palette ma-palette.json --target 7 --fix
sprezzature-colors-contrast --palette ma-palette.json --format json
```

### Simulation de daltonisme

```bash
# Trois fichiers frères : hero-protanopia.png, hero-deuteranopia.png, hero-tritanopia.png
sprezzature-colors-cvd hero.png

# Chaque fichier écrit est un PNG nommé .png, quelle que soit la source : hero.jpg donne hero-protanopia.png
sprezzature-colors-cvd hero.jpg

# Une mosaïque pour la revue de design : l'original et chaque simulation, deux par ligne
sprezzature-colors-cvd hero.png --grid --out hero-cvd-grille.png

# Deutéranopie seulement, plus une version en niveaux de gris
sprezzature-colors-cvd hero.png --types deut --grayscale
```

`--types` accepte les noms complets ou les abréviations `prot`, `deut` et `trit`, séparés par des virgules. En mode par type, `--out` est un dossier ; avec `--grid`, c'est un fichier. Les dossiers manquants sont créés.

### Palette vers Tailwind

```bash
# Bloc à coller dans une configuration existante
sprezzature-colors-palette-to-tailwind

# tailwind.config.js complet avec variantes sombres dérivées
sprezzature-colors-palette-to-tailwind --emit config --with-dark --out tailwind.config.js

# La palette académique (Okabe et Ito, lisible par les daltoniens) ou la
# palette d'impression (vérifiée en offset sur papier couché) à la place de la palette entreprise
sprezzature-colors-palette-to-tailwind --theme academic
sprezzature-colors-palette-to-tailwind --theme print
```

`--include-neutrals` ajoute les jetons Brown, Black et Gray, laissés de côté par défaut.

### Niveaux d'accessibilité

```bash
# Prévisualiser la palette maison au niveau fort contraste (7:1, WCAG AAA)
sprezzature-colors-levels --level high-contrast

# Niveaux disponibles : universal (défaut), high-contrast, monochrome,
#                       deuteranopia, protanopia, tritanopia
```

Chaque ligne affiche le nom de la couleur, son code hexadécimal à ce niveau, et son contraste sur blanc. `--theme corporate|academic|print` choisit la palette (entreprise par défaut). `--csv` lit un autre fichier de palette, avec une colonne `Base` ou `Name` et une colonne `Hexcode` ; un fichier illisible, ou sans ces colonnes, sort en 2.

---

## Utilisation en bibliothèque

```python
import sprezzature_colors as sc

# Ratio de contraste WCAG
sc.contrast_ratio_hex("#0088FF", "#FFFFFF")          # -> 3,52 (arrondi)

# Tests WCAG : échoue en AA pour le texte courant, passe pour le grand texte
sc.meets_wcag("#0088FF", "#FFFFFF", level="AA", size="normal")  # -> False
sc.meets_wcag("#0088FF", "#FFFFFF", level="AA", size="large")   # -> True

# Éclaircir / assombrir de façon perceptuelle sur l'axe de clarté OKLCH,
# teinte conservée. OKLCH est un modèle de couleur construit pour qu'un même
# pas numérique de luminosité corresponde à un même écart de clarté perçu
# par l'œil, ce que le RGB brut ne garantit pas.
sc.lighten("#0088FF", 0.15)   # -> "#4CB9FF"
sc.darken("#0088FF", 0.10)    # -> "#0068DC"

# Simulation de daltonisme pixel par pixel (sRGB 8 bits en entrée et en sortie)
sc.simulate_pixel((255, 0, 0), sc.CVD_MATRICES["protanopia"])  # -> (109, 95, 0)

# La palette maison et sa psychologie des couleurs
sc.palette_names()            # -> ['Red', 'Orange', ..., 'Gray'], 11 noms
sc.name_to_hex("Blue")        # -> "#0088FF"
sc.concept_search("trust")    # -> ['#0088FF']
sc.psychology_for("Blue")     # -> {'positive': ['Trust', ...], 'negative': [...]}
```

`sprezzature_colors.__all__` liste toute la surface publique : contraste et WCAG, lecture des codes hexadécimaux et composition alpha, conversions OKLab / OKLCH, recherche dans la palette, simulation de daltonisme, psychologie des couleurs, et `skill_path()`, le dossier du skill que livre le paquet.

---

## API HTTP

FastAPI est un cadriciel Python pour écrire des API HTTP. L'application de `sprezzature_colors.api` sert la bibliothèque en HTTP, pour qu'un système de design en TypeScript ou une tâche d'intégration continue écrite dans un autre langage lance les mêmes vérifications.

```bash
uvicorn sprezzature_colors.api:app --host 0.0.0.0 --port 8000
curl -X POST localhost:8000/v1/contrast \
     -H 'content-type: application/json' \
     -d '{"pairs":[{"foreground":"#595959","background":"#ffffff"}]}'
# {"results":[{"foreground":"#595959","background":"#ffffff","ratio":7.0,
#   "level":"AA","size":"normal","required":4.5,"passes":true}]}
```

| Route | `operation_id` | Répond à |
|---|---|---|
| `GET /health` | `health` | Le serveur tourne-t-il |
| `GET /v1/palette` | `get_palette` | La palette maison, une ligne par couleur |
| `POST /v1/contrast` | `check_contrast` | Ratio et verdict WCAG par paire (`level` AA ou AAA (les niveaux standard et renforcé des WCAG : un contraste de 4,5:1 et de 7:1 pour le texte courant), `size` normal ou large) |
| `POST /v1/cvd` | `simulate_color_blindness` | Le code hexadécimal que perçoit chaque déficience, par couleur |
| `POST /v1/adjust` | `adjust_lightness` | Couleurs plus claires (`amount` > 0) ou plus sombres (`amount` < 0), en OKLab |
| `GET /v1/psychology/{color}` | `get_color_psychology` | Associations positives et négatives d'une couleur de la palette |
| `GET /v1/concepts?keyword=` | `search_concepts` | Codes hexadécimaux de la palette associés à un concept |

Chaque route qui prend une couleur accepte un code hexadécimal ou un nom de la palette comme `"Blue"` ; tout le reste est une erreur 400. La documentation interactive est sous `/docs`.

### Docker

```bash
docker compose up -d
curl -s localhost:8000/health
docker compose run --rm api sprezzature-colors-contrast --target 7
docker compose run --rm api sprezzature-colors-cvd /work/hero.png --grid
```

L'image lance `sprezzature-colors-mcp --host 0.0.0.0 --port 8000` : un seul conteneur répond donc sur le port 8000 aux routes HTTP (`/health`, `/v1/...`) comme au point d'accès MCP (`/mcp`). Le fichier compose monte `./work` sur `/work`, en écriture, parce que la simulation écrit ses fichiers à côté de l'image source.

## Serveur MCP

```bash
sprezzature-colors-mcp                       # 127.0.0.1:8000
sprezzature-colors-mcp --host 0.0.0.0 --port 9000
```

Le serveur enveloppe la même application FastAPI avec fastapi-mcp et monte le point d'accès MCP sous `/mcp`, à côté des routes HTTP. L'`operation_id` de chaque route est le nom de l'outil MCP : les sept outils sont donc `health`, `get_palette`, `check_contrast`, `simulate_color_blindness`, `adjust_lightness`, `get_color_psychology` et `search_concepts`. `SPREZZATURE_COLORS_HOST` et `SPREZZATURE_COLORS_PORT` fixent les valeurs par défaut. L'image Docker lance ce même serveur : `docker compose up` donne aussi `/mcp`.

---

## Fonctionnalités

| Fonctionnalité | Détail |
|---|---|
| Audit de contraste WCAG | AA (4,5:1), AA grand texte (3:1), AAA (7:1) |
| Composition alpha | Premiers plans translucides `#RRGGBBAA` composités avant le calcul du ratio |
| Suggestions de correction | Voisin OKLCH le plus proche qui franchit le seuil |
| Simulation de daltonisme | Matrices de MACHADO et al. 2009 (protanopie, deutéranopie, tritanopie) |
| Vérification en niveaux de gris | Luminance relative, pour détecter les distinctions qui reposent sur la teinte seule |
| Export palette Tailwind | Bloc `brand` ou configuration `module.exports` complète, palette entreprise, académique ou d'impression |
| Niveaux d'accessibilité | universel / fort contraste / monochrome / palette adaptée à une déficience précise |
| Science de la palette | Conversions OKLab / OKLCH, fonctions de transfert sRGB ; les trois palettes de [deraison.ai/colors](https://deraison.ai/colors/) (entreprise, académique, impression), livrées dans les fichiers CSV du site |
| Psychologie des couleurs | Émotion, concepts et associations pour chacune des 12 couleurs de la palette |
| Dépendances | Une seule installation : click, FastAPI, uvicorn, Pillow, fastapi-mcp, mcp |

---

## Le seul canal qui survit

Quatre outils, une seule idée dessous.

Une couleur a trois composantes qu'on peut faire bouger : la teinte, la
saturation, la clarté. Le daltonisme rouge-vert retire la teinte.
L'impression en niveaux de gris retire la saturation. **La clarté est la
seule qu'aucun déficit, aucune imprimante et aucun écran en plein soleil ne
retire.** C'est donc sur elle que travaillent les quatre outils.

L'audit de contraste ne propose pas une autre couleur. Il fige votre teinte et
votre saturation, parcourt l'axe de clarté par centièmes, puis s'arrête à la
valeur la plus proche qui passe le seuil. Votre bleu de marque reste votre
bleu de marque : il s'éclaircit ou s'assombrit jusqu'à devenir lisible.

Les palettes dédiées à un déficit font la même chose un cran plus haut. Chaque
couleur est classée selon sa clarté *telle que ce lecteur la perçoit*, d'après
les matrices de MACHADO, puis les clartés sont réparties sur une plage
lisible. La teinte et la saturation ne bougent pas. Cela écarte les catégories pour
ce lecteur sans prouver qu'elles se distinguent : le plancher de 3:1 sur blanc
et le gamut peuvent en rapprocher deux, comme l'orange et le jaune en
deutéranopie sur la palette maison, et c'est pourquoi la forme et l'étiquette
restent à leur poste.

C'est aussi pourquoi ces palettes sont des options plutôt que le défaut.
Aucun jeu de couleurs n'est le meilleur pour la protanopie, la deutéranopie et
la tritanopie à la fois : améliorer l'écart pour un œil le referme pour un
autre. Le défaut (`universal`) est la palette déjà séparée par la clarté pour
tout le monde, la forme, l'étiquette et la position portant le reste.

---

## Sciences des couleurs

Les ratios de contraste suivent la norme WCAG 2.x : la luminance relative (à quel point une couleur paraît claire à l'œil, pas seulement ses valeurs RGB (*red, green, blue*, les trois lumières qu'un écran mélange pour chaque couleur : #FF0000 est le rouge pur) brutes) utilise la fonction de transfert gamma 2,4 que fixe la norme. Les ajustements perceptuels utilisent OKLab et OKLCH, un modèle de couleur conçu par Björn OTTOSSON (2020) précisément pour qu'un même pas numérique de luminosité corresponde au même écart de clarté perçu par l'œil, ce que le RGB brut ne garantit pas. Les matrices de simulation du daltonisme viennent de MACHADO, OLIVEIRA et FERNANDES (2009, revue de l'IEEE (*Institute of Electrical and Electronics Engineers*, la plus grande société d'ingénieurs au monde, qui publie cette revue), *IEEE Transactions on Visualization and Computer Graphics*), un article largement cité qui a mesuré comment chaque type de daltonisme transforme une couleur perçue et a publié cette transformation sous forme d'une matrice de nombres, exactement ce que stocke `CVD_MATRICES`, à sévérité maximale.

---

## Partie de la suite sprezzature

| Dépôt | Fonction |
|---|---|
| [sprezzature](https://github.com/warith-harchaoui/sprezzature) | Le hub : dix briques, leurs skills, et le site web |
| [sprezzature-colors](https://github.com/warith-harchaoui/sprezzature-colors) | Ce dépôt |
| [sprezzature-accessibility](https://github.com/warith-harchaoui/sprezzature-accessibility) | Audit statique de l'accessibilité HTML |
| [sprezzature-figures](https://github.com/warith-harchaoui/sprezzature-figures) | Visualisation de données ; applique les niveaux d'accessibilité |
| [sprezzature-ui](https://github.com/warith-harchaoui/sprezzature-ui) | Composants d'interface ; consomme l'export Tailwind |

---

## Auteur

Warith HARCHAOUI, [deraison.ai](https://deraison.ai)

Licence : *Berkeley Software Distribution*, version à trois clauses (BSD-3-Clause, une licence permissive : chacun peut utiliser, modifier et revendre le code s'il garde la mention du copyright)
