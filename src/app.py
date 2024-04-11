from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace

from hotel import Hotel
from redis_om import get_redis_connection, Migrator, NotFoundError
from src.config import setup_logger
from src.load_data_into_redis import load_hotels
from src.vector_search import find_similar_hotels
from prometheus_flask_exporter import PrometheusMetrics

logger = setup_logger()

# Initialize Flask App
app = Flask(__name__)
api = Api(app, version='1.0', title='Hotel API', description='A simple API for hotel operations', prefix='/api/v1')

# Initialize Prometheus metrics for your Flask app
metrics = PrometheusMetrics(app)
# static information as metric
metrics.info('app_info', 'Application info', version='0.0.1-gabs')

# Track the total number of hotel searches
hotel_search_similar_counter = metrics.counter(
    'hotel_searches_total', 'Total number of hotel searches',
    labels={'endpoint': lambda: request.endpoint}
)
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)


# Initialize a Namespace
ns = api.namespace('hotels', description='Hotel operations')

# Contact Model
contact_model = ns.model('Contact', {
    'phone': fields.String(required=True, description='The contact phone number'),
    'email': fields.String(required=True, description='The contact email address'),
    'country_calling_code': fields.String(description='The international country calling code'),
    'website': fields.String(description='The hotel website URL'),
    'contact_person': fields.String(description='The name of the contact person at the hotel')
})

# Reviews Model
reviews_model = ns.model('Reviews', {
    'positive': fields.String(description='Positive review highlights'),
    'negative': fields.String(description='Negative review highlights')
})

# Hotel Model
hotel_model = ns.model('Hotel', {
    'name': fields.String(required=True, description='The name of the hotel'),
    'address': fields.String(required=True, description='The address of the hotel'),
    'amenities': fields.List(fields.String, description='List of amenities provided by the hotel'),
    'contact': fields.Nested(contact_model, description='Contact information of the hotel'),
    'rating': fields.String(description='The star rating of the hotel'),
    'reviews': fields.Nested(reviews_model, description='The positive and negative reviews of the hotel')
})

# Define a model for the vector search response
vector_search_response_model = ns.model('VectorSearchResponse', {
    'similar_hotels': fields.List(fields.Nested(hotel_model), description='List of similar hotels found')
})


@app.route("/cintia")
def hello_world():
    return "<p>Hello, Bart!</p>"


# Define Hotel Resource for CRUD operations
@ns.route('/')
class HotelList(Resource):
    @ns.doc('list_hotels')
    @ns.marshal_list_with(hotel_model)
    def get(self):
        '''List all hotels'''
        return [hotel.dict() for hotel in Hotel.all()], 200

    @ns.doc('create_hotel')
    @ns.expect(hotel_model)
    @ns.marshal_with(hotel_model, code=201)
    def post(self):
        '''Create a new hotel'''
        data = ns.payload
        hotel = Hotel(**data)
        hotel.save()
        return hotel.dict(), 201


@ns.route('/<string:id>')
@ns.response(404, 'Hotel not found')
@ns.param('id', 'Hotel identifier')
class HotelResource(Resource):
    @ns.doc('get_hotel')
    @ns.marshal_with(hotel_model)
    def get(self, id):
        '''Fetch a hotel given its identifier'''
        try:
            hotel = Hotel.get(id)
            return hotel.dict(), 200
        except Hotel.DoesNotExist:
            ns.abort(404, "Hotel not found")

    @ns.doc('delete_hotel')
    @ns.response(204, 'Hotel deleted')
    def delete(self, id):
        '''Delete a hotel given its identifier'''
        try:
            Hotel.delete(id)
            return '', 204
        except Hotel.DoesNotExist:
            ns.abort(404, "Hotel not found")

    @ns.doc('update_hotel')
    @ns.expect(hotel_model)
    @ns.marshal_with(hotel_model)
    def put(self, id):
        '''Update a hotel given its identifier'''
        data = ns.payload
        try:
            hotel = Hotel.get(id)
            for key, value in data.items():
                setattr(hotel, key, value)
            hotel.save()
            return hotel.dict(), 200
        except Hotel.DoesNotExist:
            ns.abort(404, "Hotel not found")


@ns.route('/<string:id>/similar')
@ns.param('id', 'The hotel identifier to find similar hotels for')
class HotelSimilar(Resource):
    @hotel_search_similar_counter
    @ns.doc('find_similar_hotels')
    @ns.response(404, 'Hotel not found')
    @ns.marshal_with(vector_search_response_model)
    def get(self, id):
        '''Find hotels similar to a specified hotel by ID.'''
        try:
            hotel = Hotel.get(id)
        except NotFoundError:
            ns.abort(404, f"Hotel with ID {id} not found")

        similar_hotels = find_similar_hotels(hotel)
        # Assuming 'find_similar_hotels' returns a list of similar hotels
        return {'similar_hotels': [h.dict() for h in similar_hotels]}


def ensure_data_loaded():
    """Check if there are any hotels in the database, and if not, load them."""
    # Attempt to find hotels. This approach tries to fetch hotels without relying on chain calls that might not be
    # supported as expected.
    hotels = list(Hotel.find())

    if not hotels:
        logger.info("No hotels found in the database. Loading hotels...")
        load_hotels()
        logger.info("Hotels loaded successfully.")
    else:
        logger.info(f"Hotels already present in the database. Found {len(hotels)} entries.")


def ensure_indexes_created():
    """Ensure that Redis OM indexes are created."""
    logger.info("Ensuring Redis OM indexes are created...")
    Migrator().run()
    logger.info("Indexes created successfully.")


if __name__ == "__main__":
    ensure_indexes_created()  # Ensure indexes are created before checking data
    ensure_data_loaded()  # Load data if necessary
    app.run(debug=True)