import os
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
CHECKPOINT = "MBZUAI/LaMini-Flan-T5-248M"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def get_model():
    """Initialize and return the tokenizer and model with error handling"""
    try:
        logger.info(f"Loading model {CHECKPOINT} on device {DEVICE}")
        
        tokenizer = T5Tokenizer.from_pretrained(CHECKPOINT)
        model = T5ForConditionalGeneration.from_pretrained(
            CHECKPOINT,
            device_map='auto',
            torch_dtype=torch.float32,
            offload_folder="./offload"
        )
        
        if DEVICE == "cuda":
            model = model.to(DEVICE)
            
        logger.info("Model loaded successfully")
        return tokenizer, model
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

def validate_pdf(file_path):
    """Check if PDF exists and is readable"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at {file_path}")
    if os.path.getsize(file_path) == 0:
        raise ValueError("PDF file is empty")

def generate_summary(file_path):
    """Generate summary from PDF with comprehensive error handling"""
    try:
        # Validate input file
        validate_pdf(file_path)
        
        # Load model
        tokenizer, model = get_model()
        
        # Load and split PDF
        logger.info(f"Processing PDF: {file_path}")
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=50
        )
        texts = text_splitter.split_documents(pages)
        final_text = " ".join([text.page_content for text in texts])
        
        if not final_text.strip():
            raise ValueError("No text content extracted from PDF")
        
        # Generate summary
        logger.info("Generating summary...")
        inputs = tokenizer.encode(
            "summarize: " + final_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(DEVICE)
        
        summary_ids = model.generate(
            inputs,
            max_length=150,
            min_length=50,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True
        )
        
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        if not summary.strip():
            raise ValueError("Generated summary is empty")
            
        logger.info("Summary generated successfully")
        return summary
        
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}", exc_info=True)
        return f"Summary generation failed: {str(e)}"