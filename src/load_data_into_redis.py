import json
import logging
from hotel import Hotel, Contact
from sentence_transformers import SentenceTransformer
from redis_om import get_redis_connection, Migrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
redis = get_redis_connection()


def load_hotels():
    with open('../data/hotels_data_with_duplicates.json', 'r') as file:
        hotels_data = json.load(file)
        logger.info("Loaded hotel data from JSON file.")
        for index, data in enumerate(hotels_data):
            # Extend combined text with more features
            combined_text = (
                f"{data['name']} {data['address']} "
                f"{' '.join(data['amenities'])} {data['rating']} "
                f"{data['reviews']['positive']} {data['reviews']['negative']}"
            )
            embedding = model.encode(combined_text).tolist()

            hotel = Hotel(
                name=data['name'],
                address=data['address'],
                amenities=data['amenities'],
                contact=Contact(
                    phone=data['contact']['phone'],
                    email=data['contact']['email'],
                    country_calling_code=data['contact']['country_calling_code'],
                    website=data['contact'].get('website'),
                    contact_person=data['contact']['contact_person'],
                    social_media=data['contact'].get('social_media')
                ),
                rating=data['rating'],
                reviews_positive=data['reviews']['positive'],
                reviews_negative=data['reviews']['negative'],
                embedding=embedding
            )
            hotel.save()
            logger.info(f"Hotel {index + 1}/{len(hotels_data)}: '{hotel.name}' saved to Redis.")

        Migrator().run()
        logger.info("Finished loading all hotels into Redis.")


if __name__ == "__main__":
    logger.info("Starting to load hotels into Redis.")
    load_hotels()
    logger.info("Completed loading hotels into Redis.")
