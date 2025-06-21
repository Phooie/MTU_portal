import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from database.books import Resource
from langchain_huggingface import HuggingFaceEmbeddings
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self):
        self.embedding_model = None
        self.db_books = None
        self.initialized = False

    def initialize(self):
        """Lazy initialization when first needed"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Initialize embedding model
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
            )
            
            # Initialize vector DB
            self._initialize_vector_db()
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Recommendation engine initialization failed: {e}")
            self.initialized = False

    def _initialize_vector_db(self):
        """Initialize the vector database"""
        try:
            tagged_desc_path = os.path.join(os.path.dirname(__file__), 'tagged_description.txt')
            
            if not os.path.exists(tagged_desc_path):
                raise FileNotFoundError(f"Tagged descriptions file not found at {tagged_desc_path}")
            
            loader = TextLoader(tagged_desc_path)
            raw_documents = loader.load()
            
            # Clean and split documents
            raw_text = raw_documents[0].page_content
            cleaned_text = "\n".join([line.strip() for line in raw_text.split("\n") if line.strip()])
            
            splitter = CharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=0,
                separator="\n",
                keep_separator=False
            )
            
            documents = splitter.split_documents([Document(page_content=cleaned_text)])
            
            self.db_books = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_model,
                persist_directory="./chroma_db"  # Optional persistence
            )
            
            logger.info(f"Vector DB initialized with {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Vector DB initialization failed: {e}")
            raise

    def get_recommendations(self, query: str, resource_type: str = None, category: str = None, top_k: int = 5):
        """Get semantic recommendations"""
        if not self.initialized:
            self.initialize()
            if not self.initialized:
                return Resource.objects.none()
                
        try:
            recs = self.db_books.similarity_search(query, k=top_k * 3)
            matched_titles = [doc.page_content.split(' ', 1)[1].strip() for doc in recs]
            
            books_qs = Resource.objects.filter(title__in=matched_titles)
            
            if resource_type:
                books_qs = books_qs.filter(resource_type__contains=resource_type)
            if category:
                books_qs = books_qs.filter(category__iexact=category)
                
            return books_qs.order_by('?')[:top_k]
            
        except Exception as e:
            logger.error(f"Recommendation failed: {e}")
            return Resource.objects.none()

# Singleton instance
recommendation_engine = RecommendationEngine()