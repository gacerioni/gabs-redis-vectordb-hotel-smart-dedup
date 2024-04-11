from redis_om import EmbeddedJsonModel, Field, JsonModel, VectorFieldOptions
from typing import List, Optional

from src.config import vss_algorithm, vss_type, vss_dimension, vss_distance_metric


class Contact(EmbeddedJsonModel):
    phone: str = Field(index=True)
    email: str = Field(index=True)
    country_calling_code: str = Field(index=True)
    website: Optional[str] = Field(index=False)  # Optional and not indexed
    contact_person: str = Field(index=True)
    social_media: Optional[dict] = Field(index=False)  # Assuming it's a dictionary; not indexed


class Hotel(JsonModel):
    name: str = Field(index=True, full_text_search=True)
    address: str = Field(index=True, full_text_search=True)
    amenities: List[str] = Field(index=False)  # If you need this searchable, consider alternative approaches
    contact: Contact  # Embedded model for contact info
    rating: str = Field(index=True)
    reviews_positive: str = Field(index=True, full_text_search=True)
    reviews_negative: str = Field(index=True, full_text_search=True)
    embedding: List[float] = Field(index=True, vector_options=VectorFieldOptions(
        algorithm=vss_algorithm,
        type=vss_type,
        dimension=vss_dimension,  # Assuming a dimension of 384 as an example
        distance_metric=vss_distance_metric,
    ))
