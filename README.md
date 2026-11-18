# Projet de compilation

## Partie 1 — Grammaire LL(1) des expressions régulières

### 1. Grammaire étudiée

La grammaire fournie est obtenue par élimination de la récursivité à gauche.
`SYMBOLE` désigne un caractère alphanumérique et `$` la fin de l'entrée.

```text
R  → T R'
R' → '|' T R' | ε
T  → F T'
T' → F T' | ε
F  → A F'
F' → '*' F' | '+' F' | '?' F' | ε
A  → '(' R ')' | SYMBOLE | '@'
```

### 2. Ensembles PREMIER et SUIVANT

#### 2.1. Calcul de PREMIER

- `PREMIER(A) = { (, SYMBOLE, @ }`, d'après les trois productions de `A`.
- `PREMIER(F) = PREMIER(A)`, car `F → A F'` et `A` n'est pas annulable.
- `PREMIER(T) = PREMIER(F)` et `PREMIER(R) = PREMIER(T)`, pour la même raison.
- `PREMIER(F') = { *, +, ?, ε }`.
- `PREMIER(T') = PREMIER(F) ∪ { ε }`.
- `PREMIER(R') = { |, ε }`.

#### 2.2. Calcul de SUIVANT

- `SUIVANT(R)` contient `$` (symbole de départ) et `)` (via `A → '(' R ')'`).
- `SUIVANT(R') = SUIVANT(R)`, car `R'` termine la production de `R`.
- `SUIVANT(T) = (PREMIER(R') \ {ε}) ∪ SUIVANT(R)`, car `R'` est annulable.
- `SUIVANT(T') = SUIVANT(T)`.
- `SUIVANT(F) = (PREMIER(T') \ {ε}) ∪ SUIVANT(T)`, car `T'` est annulable.
- `SUIVANT(F') = SUIVANT(F)`.
- `SUIVANT(A) = (PREMIER(F') \ {ε}) ∪ SUIVANT(F)`, car `F'` est annulable.

| Non-terminal | PREMIER | SUIVANT |
|---|---|---|
| `R` | `( SYMBOLE @` | `) $` |
| `R'` | `\| ε` | `) $` |
| `T` | `( SYMBOLE @` | `\| ) $` |
| `T'` | `( SYMBOLE @ ε` | `\| ) $` |
| `F` | `( SYMBOLE @` | `( SYMBOLE @ \| ) $` |
| `F'` | `* + ? ε` | `( SYMBOLE @ \| ) $` |
| `A` | `( SYMBOLE @` | `* + ? ( SYMBOLE @ \| ) $` |

### 3. PREMIER de chaque production

Pour une production `X → α`, `PREMIER(α)` est le PREMIER de la partie droite.
Si `α` est annulable, on y ajoute `SUIVANT(X)`. C'est cet ensemble qui remplit
la table.

| Production | PREMIER de la production |
|---|---|
| `R → T R'` | `( SYMBOLE @` |
| `R' → '|' T R'` | `\|` |
| `R' → ε` | `SUIVANT(R') = ) $` |
| `T → F T'` | `( SYMBOLE @` |
| `T' → F T'` | `( SYMBOLE @` |
| `T' → ε` | `SUIVANT(T') = \| ) $` |
| `F → A F'` | `( SYMBOLE @` |
| `F' → '*' F'` | `*` |
| `F' → '+' F'` | `+` |
| `F' → '?' F'` | `?` |
| `F' → ε` | `SUIVANT(F') = ( SYMBOLE @ \| ) $` |
| `A → '(' R ')'` | `(` |
| `A → SYMBOLE` | `SYMBOLE` |
| `A → '@'` | `@` |

### 4. Table d'analyse prédictive

Chaque case `M[X, t]` contient la production `X → α` telle que
`t ∈ PREMIER(α)` (ou `α` annulable et `t ∈ SUIVANT(X)`). Les cases vides
correspondent à des erreurs syntaxiques.

|  | `(` | `SYMBOLE` | `@` | `\|` | `*` | `+` | `?` | `)` | `$` |
|---|---|---|---|---|---|---|---|---|---|
| `R` | `T R'` | `T R'` | `T R'` |  |  |  |  |  |  |
| `R'` |  |  |  | `'|' T R'` |  |  |  | `ε` | `ε` |
| `T` | `F T'` | `F T'` | `F T'` |  |  |  |  |  |  |
| `T'` | `F T'` | `F T'` | `F T'` | `ε` |  |  |  | `ε` | `ε` |
| `F` | `A F'` | `A F'` | `A F'` |  |  |  |  |  |  |
| `F'` |  | `ε` | `ε` | `ε` | `'*' F'` | `'+' F'` | `'?' F'` | `ε` |  |
| `A` | `'(' R ')'` | `SYMBOLE` | `'@'` |  |  |  |  |  |  |

#### 4.1. Preuve de l'absence de conflit

Chaque case contient au plus une production, donc la grammaire est LL(1).
Pour les non-terminaux à plusieurs productions, il suffit de vérifier que les
PREMIER des productions sont deux à deux disjoints :

- `R'` : `{ | } ∩ { ), $ } = ∅`
- `T'` : `{ (, SYMBOLE, @ } ∩ { |, ), $ } = ∅`
- `F'` : `{ * }`, `{ + }`, `{ ? }` et `{ (, SYMBOLE, @, |, ), $ }` sont deux à deux disjoints
- `A` : `{ ( }`, `{ SYMBOLE }`, `{ @ }` sont deux à deux disjoints

Les non-terminaux `R`, `T` et `F` n'ont qu'une seule production ; ils ne
peuvent pas être en conflit.

### 5. Grammaire de départ et transformation

#### 5.1. Grammaire naturelle (récursive à gauche)

```text
R → R '|' T | T
T → T F | F
F → F '*' | F '+' | F '?' | A
A → '(' R ')' | SYMBOLE | '@'
```

Cette forme traduit directement l'associativité à gauche de l'union et de la
concaténation, ainsi que la priorité `| < concaténation < opérateurs postfixés`.

#### 5.2. Transformation appliquée

Une analyse descendante boucle indéfiniment sur une règle récursive à gauche
(`R` appellerait `R` sans consommer de jeton). On applique la transformation
classique :

```text
X → X α | β
```

est remplacée par :

```text
X  → β X'
X' → α X' | ε
```

Pour `R`, `α = '|' T` et `β = T`. Pour `T`, `α = F` et `β = F`. Pour `F`,
`α` est l'un des opérateurs `*`, `+`, `?` et `β = A`. On retrouve exactement
`R'`, `T'` et `F'` de la grammaire fournie. Le langage reconnu est inchangé.

### 6. Pourquoi tester PREMIER(F) dans T' ?

La concaténation est implicite : il n'y a aucun symbole entre `r` et `s` dans
`rs`. Pour décider si `T'` continue (`T' → F T'`) ou s'arrête (`T' → ε`), le
seul indice est le jeton courant. On continue si et seulement s'il peut
commencer un `F`, c'est-à-dire s'il appartient à
`PREMIER(F) = { (, SYMBOLE, @ }`.

Le choix est déterministe car `PREMIER(F)` est disjoint de
`SUIVANT(T') = { |, ), $ }`. Un jeton comme `|` ou `)` ne peut jamais débuter
un facteur : il signale la fin de la concaténation en cours.

### 7. Détection des erreurs

#### 7.1. Cas de `a)`

L'analyse de `a` réussit. Sur `)`, `F'`, `T'` et `R'` choisissent `ε`, car `)`
appartient à leur SUIVANT. `R` se termine donc normalement, mais il reste un
jeton non consommé. L'erreur est détectée après l'analyse de `R`, par le test
de fin d'entrée : on attend `$` et on trouve `)`.

#### 7.2. Cas de `a||b`

`R'` lit le premier `|` (case `M[R', |]`) puis appelle `T` avec le second `|`
comme jeton courant. La case `M[T, |]` est vide : l'erreur est détectée à la
position 3, avec `(`, `SYMBOLE` ou `@` attendus.

#### 7.3. Synthèse

| Entrée | Où est l'erreur détectée | Jetons attendus |
|---|---|---|
| `a)` | Test de fin d'entrée après `R` | fin de l'expression, `\|`, `*`, `+`, `?`, `(`, `SYMBOLE`, `@` |
| `a||b` | Case vide `M[T, \|]` | `(`, `SYMBOLE`, `@` |
| `(ab` | Attente de `)` dans `A` | `)` (et les continuations possibles) |
| `*a`, `\|a` | Case vide `M[R, *]` ou `M[R, \|]` | `(`, `SYMBOLE`, `@` |
| `()` | Case vide `M[R, )]` (appel de `R` depuis `A`) | `(`, `SYMBOLE`, `@` |
| `a(` | Case vide `M[A, $]` | `(`, `SYMBOLE`, `@` |
