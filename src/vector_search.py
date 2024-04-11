from src.config import REDIS_VSS_REDIS_OM_INDEX_NAME
import numpy as np
import logging
from redis_om import get_redis_connection, NotFoundError
from redis.commands.search.query import Query
from hotel import Hotel  # Ensure Hotel class is imported correctly

# Setup logging and Redis connection as before
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
redis = get_redis_connection()
hotel_vss_idx = REDIS_VSS_REDIS_OM_INDEX_NAME  # Update with your actual index name


def find_similar_hotels(hotel: Hotel):
    similar_hotels = []
    try:
        if not hasattr(hotel, 'embedding') or not hotel.embedding:
            logger.error(f"No embedding found for hotel with ID: {hotel.pk}.")
            return []

        embedding_as_blob = np.array(hotel.embedding, dtype=np.float32).tobytes()
        query = Query(f"*=>[KNN 3 @embedding $vec AS score]").sort_by("score").paging(0, 3).dialect(2)
        results = redis.ft(hotel_vss_idx).search(query, query_params={"vec": embedding_as_blob})

        logger.info(f"Comparing hotels similar to {hotel.pk}:\n")
        for doc in results.docs:
            hotel_pk = doc.id.split(':')[-1]
            try:
                similar_hotel = Hotel.get(hotel_pk)
                similar_hotels.append(similar_hotel)  # Add the hotel to the list of similar hotels

                # Log details about the similar hotel
                logger.info(f"Similar Hotel ID: {similar_hotel.pk}")
                logger.info(f"Name: {similar_hotel.name} (Score: {doc.score})")
                logger.info(f"Address: {similar_hotel.address}")
                logger.info(f"Rating: {similar_hotel.rating}")
                logger.info("Amenities: " + ", ".join(similar_hotel.amenities))
                if similar_hotel.name == hotel.name:
                    logger.info("This hotel might be a duplicate based on the name.")
                logger.info("--------------------------------------------------\n")

            except NotFoundError:
                logger.error(f"Hotel with PK {hotel_pk} not found.")
    except Exception as e:
        logger.error(f"Failed to find similar hotels for {hotel.pk}: {e}")
        return []

    return similar_hotels  # Return the list of similar hotels


if __name__ == "__main__":
    # Example of using a Hotel object directly
    hotel_pk = "01HV7EW0PDGHEQD255HXMR4MHJ"  # Use an actual PK from your Redis database
    try:
        hotel = Hotel.get(hotel_pk)
        #logger.info(hotel)
        logger.info("Starting to find similar hotels.")
        find_similar_hotels(hotel)
    except NotFoundError:
        logger.error(f"Hotel with PK {hotel_pk} not found.")
