from faker import Faker
import json
import numpy as np

#fake = Faker('es_CL')
fake = Faker('en_US')

HOTEL_JSON_LIST_OUTPUT_FILE = '../../data/hotels_data_with_duplicates.json'
HOTEL_JSON_LIST_FILE_MODE = 'w'
HOTEL_JSON_LIST_UNIQUE_HOTELS = 2500
HOTEL_JSON_LIST_VARIATIONS_OF_EACH_HOTEL = 3


# Function to create a hotel JSON object
def create_hotel():
    name_base = fake.company() + " Hotel"
    amenities = np.random.choice(
        ["Free WiFi", "Pool", "Spa", "Gym", "Pet Friendly", "Room Service", "Restaurant", "Bar", "Airport Shuttle",
         "Family Rooms", "Non-Smoking Rooms", "Breakfast"], size=np.random.randint(3, 8), replace=False).tolist()
    hotel = {
        "name": name_base,
        "address": fake.address().replace("\n", ", "),
        "amenities": amenities,
        "contact": {
            "phone": fake.phone_number(),
            "email": fake.email(),
            "country_calling_code": fake.country_calling_code(),
            "website": fake.uri(),
            "contact_person": fake.name()
        },
        "rating": f"{np.random.randint(1, 6)} stars",
        "reviews": {
            "positive": fake.sentence(),
            "negative": fake.sentence()
        }
    }
    return hotel


# Function to create variations of a given hotel
def create_hotel_variations(hotel, num_variations=HOTEL_JSON_LIST_VARIATIONS_OF_EACH_HOTEL):
    variations = [hotel]  # include the original hotel
    for _ in range(num_variations):
        variation = hotel.copy()
        variation_name_modifiers = ['Resort', 'Inn', 'Suites', 'Lodge', 'Place', 'BnB']
        variation_modifier = fake.random.choice(variation_name_modifiers)
        variation['name'] = f"{variation['name']} {variation_modifier}"

        # Slightly modify amenities
        if len(variation['amenities']) > 2:  # Ensure there are enough amenities to modify
            dropped_amenity = variation['amenities'].pop(fake.random.randint(0, len(variation['amenities']) - 1))
            new_amenity = fake.random.choice(["Spa", "Gym", "Pet Friendly", "Bar", "Airport Shuttle", "Breakfast"])
            if new_amenity not in variation['amenities']:
                variation['amenities'].append(new_amenity)

        variations.append(variation)
    return variations


def main():
    unique_hotels = [create_hotel() for _ in range(HOTEL_JSON_LIST_UNIQUE_HOTELS)]

    all_hotels = []
    for hotel in unique_hotels:
        all_hotels.extend(create_hotel_variations(hotel, num_variations=np.random.randint(1, 3)))

    np.random.shuffle(all_hotels)

    with open(HOTEL_JSON_LIST_OUTPUT_FILE, HOTEL_JSON_LIST_FILE_MODE) as f:
        json.dump(all_hotels, f, indent=4)

    print("Hotel data with duplicates generated and saved to 'hotels_data_with_duplicates.json'.")


if __name__ == "__main__":
    main()
