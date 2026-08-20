# Paysage

Les outils d'accessibilité des couleurs se répartissent en deux familles
selon ce qu'ils vérifient. Un **contrôleur de contraste et de daltonisme**
regarde les pixels affichés ou une couleur hexadécimale résolue, et se
demande si deux couleurs sont assez éloignées, pour un œil ordinaire ou pour
une personne atteinte d'une déficience de la vision des couleurs. Un
**pipeline de jetons de design** regarde la source de vérité d'une palette
(un CSV, un fichier JSON, une bibliothèque Figma) et se demande comment
l'amener dans un système de build sans recopier des codes hexadécimaux à la
main. `sprezzature-colors` fait les deux à dessein, parce que les deux
problèmes partagent la même science des couleurs sous-jacente (transfert
sRGB, luminance WCAG, OKLab/OKLCH), et que la garder dans un seul petit
paquet évite de l'écrire deux fois.

## Comparaison des outils

| Outil | Type | Navigateur requis | Suggestions de correction | Compatible CI | Python |
|---|---|---|---|---|---|
| **sprezzature-colors** | Audit de contraste + simulation CVD + export de jetons | Non | Oui (voisin OKLCH) | Oui | Oui |
| axe-core / Lighthouse | Contrôle de contraste sur le DOM en direct | Oui | Non | Oui (via CLI) | Non |
| Stark (plugin Figma/Sketch) | Contraste + simulation CVD dans l'outil de design | Non (plugin) | Non | Non | Non |
| Coblis / Color Oracle | Simulateur CVD autonome | Non | Non | Non | Non (Color Oracle : appli native) |
| Style Dictionary | Pipeline de jetons de design | Non | Sans objet | Oui | Non (Node) |

### Notes par dimension

| Dimension | sprezzature-colors | axe-core | Stark | Style Dictionary |
|---|---|---|---|---|
| Couverture du contraste | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Sans objet |
| Simulation CVD | ⭐⭐⭐⭐ | Sans objet | ⭐⭐⭐⭐ | Sans objet |
| Export de jetons | ⭐⭐⭐ | Sans objet | Sans objet | ⭐⭐⭐⭐⭐ |
| Installation sans dépendance | ⭐⭐⭐⭐⭐ | ⭐⭐ | Sans objet (plugin) | ⭐⭐⭐ |
| Suggestions de correction | ⭐⭐⭐⭐ | ⭐ | ⭐ | Sans objet |

## Quand utiliser quoi

Utilisez `sprezzature-colors` comme **porte CI** pour les deux problèmes à
la fois : `audit_contrast.py` fait échouer le build sur une vraie
régression de contraste, `simulate_cvd.py --grid` produit une image qu'un
relecteur peut juger d'un coup d'œil, et `palette_to_tailwind.py` garde le
`tailwind.config.js` de chaque projet consommateur généré depuis le même
`palette.csv`, plutôt que de laisser chaque projet dériver de son côté.

axe-core (ou l'audit d'accessibilité de Lighthouse) est le bon outil pour
le contraste sur un DOM en direct, puisqu'il lit les styles calculés d'une
page réellement affichée et attrape les cas où une cascade CSS ou une
opacité changent la couleur rendue d'une façon qu'un contrôle statique de
palette ne peut pas voir.

Stark et Color Oracle conviennent à un designer qui travaille dans Figma ou
Sketch, pour prévisualiser une déficience de la vision des couleurs en
direct pendant qu'une maquette est encore en train de se dessiner, avant
même qu'aucun code n'existe pour lancer `simulate_cvd.py`.

Style Dictionary convient une fois qu'un système de jetons de design doit
publier vers de nombreuses plateformes à la fois (iOS, Android, web,
plusieurs frameworks CSS) ; `palette_to_tailwind.py` reste volontairement
plus étroit, un CSV en entrée, un bloc Tailwind en sortie, parce que c'est
le seul export dont cette suite a besoin aujourd'hui.
