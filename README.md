# 📘 Moteur de Recommandation de Livres (IA + MongoDB + Streamlit)

## 📚 Présentation du projet

Ce projet consiste à développer une application web intelligente permettant de recommander des livres grâce à la recherche sémantique. L'utilisateur saisit une phrase décrivant le type de livre recherché, et l'application renvoie automatiquement les œuvres les plus pertinentes en se basant sur le sens de la phrase, et non sur des mots-clés.

Le système utilise :
* **MongoDB Atlas** pour stocker une base de livres
* **Sentence Transformers** pour encoder les descriptions en vecteurs
* La **similarité cosinus** pour comparer la requête aux livres
* **Streamlit** pour l'interface utilisateur

Ce projet montre comment créer un moteur de recommandation moderne basé sur l'IA et les embeddings.

---

## 🧠 Logique générale du moteur de recommandation

### 1. Chargement des données
L'application récupère les livres dans MongoDB (Title, Author, Category, Description, Year, Rating).

### 2. Vectorisation
Chaque description est transformée en vecteur numérique (embedding) à l'aide du modèle `paraphrase-multilingual-mpnet-base-v2`.

### 3. Requête utilisateur
Le texte saisi est également converti en embedding.

### 4. Calcul de similarité cosinus
On compare l'embedding de la requête avec tous les embeddings des livres pour mesurer leur proximité sémantique.

#### 🔢 Formule utilisée (similarité cosinus)

$$\cos(\theta) = \frac{\vec{q} \cdot \vec{d}}{\|\vec{q}\| \, \|\vec{d}\|}$$

Avec :

* **Produit scalaire** :
  
  $$\vec{q} \cdot \vec{d} = \sum_{i=1}^{n} q_i d_i$$

* **Normes** :
  
  $$\|\vec{q}\| = \sqrt{\sum_{i=1}^{n} q_i^2}$$
  
  $$\|\vec{d}\| = \sqrt{\sum_{i=1}^{n} d_i^2}$$

Le résultat est compris entre :
* **+1** → très similaire
* **0** → pas de lien
* **-1** → opposé (rare pour ce type d'embeddings)

### 5. Tri des résultats
Les livres sont classés du plus pertinent au moins pertinent et affichés dans l'interface.

---

# 📌 Modèle utilisé : paraphrase-multilingual-mpnet-base-v2

## 🔹 Description générale

`paraphrase-multilingual-mpnet-base-v2` est un modèle **Sentence Transformers** qui transforme des phrases en vecteurs numériques représentant leur sens, permettant une comparaison sémantique entre textes.

---

## 🌍 Modèle multilingue

Le modèle comprend plus de **50 langues**, dont le français. Il gère efficacement des descriptions de livres variées, quel que soit le style, la longueur ou la langue utilisée.

---

## 🧠 Basé sur MPNet

Construit sur l'architecture **MPNet**, une version améliorée de BERT, le modèle offre :
- une meilleure compréhension du contexte
- une cohérence sémantique plus forte
- des représentations vectorielles plus riches

---

## 🔍 Optimisé pour la similarité sémantique

Entraîné sur des paires de phrases paraphrasées, il peut :
- détecter des textes ayant le même sens
- mesurer leur similarité
- produire des embeddings directement comparables via la **similarité cosinus**

---

## 🗂️ Structure du projet
```
.
├── livre_app.py        # Application Streamlit
├── README.md           # Documentation du projet
└── screenshots/        # Captures de l'application
```

---

## ⚙️ Étapes du projet

### ✔️ 1. Création de la base MongoDB
* Cluster Atlas
* Base `livre_database`
* Collection `livres`
* Import des documents JSON

![Base de données de livres dans mongo Atlas](screenshots/livres_atlas_data.png)


### ✔️ 2. Développement de l'IA
* Chargement du modèle SentenceTransformer
* Vectorisation des descriptions
* Calcul des similarités cosinus

### ✔️ 3. Création de l'interface Streamlit
* Barre de recherche
* Résultats affichés proprement
* Pertinence, auteur, catégorie, résumé…

![Démo_application](screenshots/capture_application.png)

### ✔️ 4. Test et déploiement local

---

## ▶️ Comment exécuter l'application

### 1️⃣ Activer l'environnement virtuel

**Windows PowerShell :**
```powershell
.\env\Scripts\Activate.ps1
```

### 2️⃣ Lancer l'application
```bash
streamlit run livre_app.py
```

---

## 📦 Dépendances principales

* `streamlit`
* `pymongo`
* `sentence-transformers`
* `scikit-learn`
* `numpy`

---

# Méthode 2 : Recherche Vectorielle via MongoDB Atlas

**Alternative avancée pour la recherche sémantique**

---

## 📖 Description

Cette seconde approche remplace la recherche sémantique locale (calculée en Python avec la similarité cosinus) par une **recherche vectorielle** réalisée directement dans **MongoDB Atlas**, grâce à un index vectoriel optimisé.

---

## ⭐ Points clés de cette méthode

### 🗄️ Stockage des embeddings
Les embeddings sont **stockés dans MongoDB**, et non en mémoire Python.

### 🚀 Atlas Vector Search
La recherche sémantique utilise **Atlas Vector Search** basé sur l'algorithme **HNSW** (Hierarchical Navigable Small World) :
- ⚡ Plus rapide que la recherche linéaire
- 📈 Hautement scalable
- 🎯 Optimisé pour les grandes dimensions vectorielles

### 🔍 Recherche distribuée
Le moteur compare la requête aux vecteurs stockés via la **similarité cosinus**, mais de manière **distribuée** et optimisée.

### 📊 Scalabilité
Cette approche est **scalable** : elle supporte des **dizaines de milliers à des millions de documents** sans dégradation des performances.

### 🤖 Pipeline RAG
Le résultat de la recherche alimente un **modèle LLM (Llama 3)** → création d'un pipeline **RAG (Retrieval-Augmented Generation)**.

### 📈 Score de pertinence
MongoDB renvoie un **score de pertinence** pour chaque document, basé sur la **proximité vectorielle**.

### 💪 Robustesse
Plus robuste que la première méthode, qui calculait les similarités **manuellement en Python** et ne convenait qu'à de **petits datasets**.

---

## 🏗️ Architecture du système

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Sentence Transformer   │
│  (Generate Embedding)   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  MongoDB Atlas          │
│  Vector Search (HNSW)   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Top K Documents        │
│  (with scores)          │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  LLM (Llama 3)          │
│  Generate Response      │
└─────────────────────────┘
```

# 🔎 Logique de la 2ème approche

---

Cette approche suit un pipeline en **4 étapes** :

---

## 1️⃣ Préparation des données (offline)

* Chaque description de webtoon/manga est transformée en **embedding** grâce au modèle `paraphrase-multilingual-mpnet-base-v2`.
* Le script `generate_embeddings.py` ajoute un champ `"embedding"` à chaque document dans MongoDB.

➡️ **La base contient maintenant du texte et des vecteurs prêts pour la recherche sémantique.**

---

## 2️⃣ Indexation vectorielle dans MongoDB Atlas

* Un **index vectoriel** `vector_index` est créé sur le champ `"embedding"`.
* MongoDB peut désormais effectuer une **recherche par similarité** directement dans la base.

---

## 3️⃣ Recherche sémantique (dans Streamlit – rag_manga.py)

Lorsqu'un utilisateur pose une question dans l'application :

* Le texte est converti en **vector** (`queryVec`) par le même modèle.
* MongoDB exécute un `$vectorSearch` :
   * Compare le vecteur utilisateur aux embeddings de la base.
   * Retourne les documents les plus proches + un **score de pertinence**.

➡️ **C'est MongoDB (et non Python) qui calcule la similarité cosinus via HNSW.**

---

## 4️⃣ Génération de réponse (RAG)

* Les webtoons les plus pertinents sont envoyés au **LLM Llama 3** via **Groq**.
* Le modèle utilise uniquement ce contexte pour générer une réponse adaptée.

➡️ **Le système combine retrieval + génération → c'est du RAG.**
