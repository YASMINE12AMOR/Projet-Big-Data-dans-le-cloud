import streamlit as st
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
import os

# ---------------------------------------------------------
# 1. CONFIGURATION GÉNÉRALE
# ---------------------------------------------------------

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# model="llama-3.1-8b-instant"

st.set_page_config(page_title="RAG Webtoon & Manga", page_icon="🦙")

# ---------------------------------------------------------
# 2. INITIALISATION DES SERVICES
# ---------------------------------------------------------

@st.cache_resource
def get_mongo_collection():
    """Connexion à MongoDB Atlas."""
    client = MongoClient(MONGO_URI)
    db = client["Livres_indexes_database"]
    return db["indexed_manga"]  # adapte selon ta collection


@st.cache_resource
def get_embedding_model():
    """Modèle pour convertir la requête en embedding."""
    return SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")


@st.cache_resource
def get_llm():
    """Connexion à l'API Groq (LLama 3)."""
    return Groq(api_key=GROQ_API_KEY)


collection = get_mongo_collection()
embedder = get_embedding_model()
llm_client = get_llm()

# ---------------------------------------------------------
# 3. RECHERCHE VECTORIELLE MONGODB ATLAS
# ---------------------------------------------------------

def vector_search(user_query, limit=5):
    """Recherche sémantique dans MongoDB Atlas via $vectorSearch."""
    
    # A. Encoder la question
    query_vec = embedder.encode(user_query).tolist()

    # B. Pipeline d'agrégation
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",   # doit correspondre à ton index Atlas
                "path": "embedding",       # champ contenant les embeddings
                "queryVector": query_vec,
                "numCandidates": 200,      # ANN (plus haut = plus précis)
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "Title": 1,
                "Author": 1,
                "Category": 1,
                "Description": 1,
                "Year": 1,
                "Rating": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    return results


# ---------------------------------------------------------
# 4. GÉNÉRATION DE RÉPONSE (LLM + CONTEXTE)
# ---------------------------------------------------------

def generate_rag_response(query, docs):
    """Construit un contexte et interroge Llama 3 pour générer la réponse."""
    
    # Construction du contexte textuel
    context_text = ""
    for d in docs:
        context_text += (
            f"Titre: {d.get('Title')}\n"
            f"Auteur: {d.get('Author')}\n"
            f"Catégorie: {d.get('Category')}\n"
            f"Résumé: {d.get('Description')}\n"
            f"---\n"
        )

    system_prompt = (
        "Tu es un expert en mangas et webtoons. "
        "Utilise uniquement les informations du contexte fourni pour répondre. "
        "Si la réponse ne s’y trouve pas, dis-le clairement. Réponds en français."
    )

    user_message = f"""
Contexte :
{context_text}

Question utilisateur :
{query}
"""

    # Appel LLM Groq
    response = llm_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content


# ---------------------------------------------------------
# 5. INTERFACE UTILISATEUR STREAMLIT
# ---------------------------------------------------------

st.title("🦙📚 RAG Webtoon & Manga — MongoDB Atlas + Llama 3")
st.markdown("Pose ta question sur un webtoon, un manga ou un thème, et l’IA va chercher dans la base.")

user_query = st.text_input("💬 Votre question :", 
                           placeholder="Ex : Un webtoon d'action avec une académie magique ?")

if user_query:
    # A. RETRIEVAL
    st.info("🔍 Recherche des webtoons/mangas pertinents...")
    try:
        retrieved_docs = vector_search(user_query)
    except Exception as e:
        st.error(f"Erreur MongoDB : {e} — Vérifie ton index vectoriel dans Atlas.")
        st.stop()

    if not retrieved_docs:
        st.warning("Aucun document pertinent trouvé dans la base.")
        st.stop()

    st.success(f"{len(retrieved_docs)} documents pertinents trouvés.")

    # B. GENERATION
    st.info("🤖 Génération d'une réponse avec Llama 3...")
    answer = generate_rag_response(user_query, retrieved_docs)

    st.markdown("## 📘 Réponse de l’IA")
    st.write(answer)

    # C. SOURCES
    st.markdown("## 📚 Les Webtoons trouvés")
    for doc in retrieved_docs:
        st.markdown(f"### {doc.get('Title')} — Score: {doc.get('score'):.4f}")
        st.caption(doc.get("Description"))
        st.divider()