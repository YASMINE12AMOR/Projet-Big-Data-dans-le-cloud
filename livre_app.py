import streamlit as st
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
import os 

# --- CHARGEMENT DES VARIABLES D'ENVIRONNEMENT ---
load_dotenv()  # charge le fichier .env

MONGO_URI = os.getenv("MONGO_URI")


# Configuration de la page Streamlit
st.set_page_config(page_title="Book Recommender", page_icon="📚")

# --- CONNEXIONS & CHARGEMENT DES DONNÉES ---

@st.cache_resource
def get_db_collection():
    client = MongoClient(MONGO_URI)
    # Ta base et ta collection réelles :
    db = client["livre_database"]
    return db["livres"]

@st.cache_resource
def get_model():
    return SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
    #return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data
def load_books_and_embeddings():
    """
    Charge tous les livres depuis MongoDB et calcule les embeddings
    de la Description en une fois (pour les réutiliser ensuite).
    """
    collection = get_db_collection()
    # On récupère tous les documents, sans _id (optionnel)
    books = list(collection.find({}, {"_id": 0}))
    
    # On s'assure que les champs existent (Title, Description, etc.)
    # On peut filtrer pour éviter les docs incomplets
    books = [
        b for b in books
        if "Description" in b and isinstance(b["Description"], str) and b["Description"].strip() != ""
    ]
    
    model = get_model()
    descriptions = [b["Description"] for b in books]
    embeddings = model.encode(descriptions, convert_to_numpy=True)

    return books, embeddings

collection = get_db_collection()
model = get_model()
books, embeddings = load_books_and_embeddings()

# --- FONCTION DE RECHERCHE SÉMANTIQUE ---

def semantic_search(query: str, top_k: int = 5):
    """
    Encode la requête et calcule la similarité cosinus avec tous
    les livres (basé sur la Description). Renvoie les top_k.
    """
    if len(books) == 0:
        return []

    query_vec = model.encode(query, convert_to_numpy=True)

    # Similarité cosinus
    # cos_sim(a,b) = (a·b) / (||a|| * ||b||)
    query_norm = np.linalg.norm(query_vec)
    emb_norms = np.linalg.norm(embeddings, axis=1)
    sims = np.dot(embeddings, query_vec) / (emb_norms * query_norm + 1e-10)

    # Indices triés du plus pertinent au moins pertinent
    top_indices = np.argsort(sims)[::-1][:top_k]

    results = []
    for idx in top_indices:
        book = books[idx].copy()
        book["score"] = float(sims[idx])
        results.append(book)
    return results

# --- INTERFACE UTILISATEUR ---

st.title("📚 Moteur de Recommandation IA")
st.markdown("Trouvez un livre grâce à la **recherche sémantique** (sur le résumé en français).")

# Info sur le nombre de livres en base
st.info(f"Base de données chargée avec **{len(books)}** livres.")

# Barre de recherche
query = st.text_input(
    "Que cherchez-vous ?",
    placeholder="Ex: Une histoire de magie dans une école..."
)

if query:
    with st.spinner("Analyse sémantique en cours..."):
        results = semantic_search(query, top_k=5)

    st.subheader(f"Résultats pour : '{query}'")

    if not results:
        st.warning("Aucun résultat trouvé. Vérifie que la base contient bien des descriptions.")
    else:
        for book in results:
            with st.container():
                # Titre + auteur
                st.markdown(f"### 📖 {book.get('Title', 'Titre inconnu')}")
                st.markdown(
                    f"**Auteur :** {book.get('Author', 'Inconnu')} | "
                    f"**Catégorie :** {book.get('Category', 'N/A')}"
                )

                # Rating / Année / Score
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    rating = book.get("Rating", "N/A")
                    st.write(f"⭐ **Note :** {rating}/5" if rating != "N/A" else "⭐ **Note :** N/A")
                with col2:
                    year = book.get("Year", "N/A")
                    st.write(f"📅 **Année :** {year}")
                with col3:
                    st.write(f"📊 **Pertinence :** {book['score']:.2f}")

                # Description
                with st.expander("Lire le résumé"):
                    st.write(book.get("Description", "Pas de résumé disponible."))

                st.divider()
else:
    st.caption("💡 Tape une phrase ou un thème pour lancer une recherche, par ex. : *un roman historique avec de la guerre* ou *un thriller psychologique sombre*.")
