from dotenv import load_dotenv
import os
import logging

from redis_om import VectorFieldOptions

# Load environment variables from .env file
load_dotenv()

# Configuration for Redis
REDIS_URL = os.getenv('GABS_REDIS_URL', 'redis://localhost:6379')

# Configuration for Vector Search Service (VSS)
REDIS_VSS_REDIS_OM_INDEX_NAME = os.getenv('GABS_REDIS_VSS_REDIS_OM_INDEX_NAME', ':hotel.Hotel:index')

# Configuration for OpenAI API Key - If I ever use it to combo LLM with this.
#OPENAI_API_KEY = os.getenv('GABS_OPENAI_API_KEY', '')


# VECTOR SEARCH PARAMETERS
#vss_embedding_model = "Salesforce/SFR-Embedding-Mistral"
#vss_embedding_model = "sentence-transformers/gtr-t5-xl"
vss_embedding_model = "sentence-transformers/all-mpnet-base-v2"
vss_algorithm = VectorFieldOptions.ALGORITHM.HNSW
vss_type = VectorFieldOptions.TYPE.FLOAT32
vss_dimension = 768
vss_distance_metric = VectorFieldOptions.DISTANCE_METRIC.COSINE


# Setup logging configuration
def setup_logger():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)

    # Optional: Here's how you can add a file handler to also log to a file
    file_handler = logging.FileHandler('application.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    return logger
