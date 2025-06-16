import uuid
from categories.models import MongoDBConnection, Category

class Product:
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = str(data.get('id', uuid.uuid4()))
        self.name = data.get('name', '')
        self.price = data.get('price', 0.0)
        self.category_id = data.get('category_id', '')
        self.description = data.get('description', '')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category_id': self.category_id,
            'description': self.description
        }

    @staticmethod
    def create(product_data):
        category_id = product_data.get('category_id')
        if category_id and not Category.get_by_id(category_id):
            raise ValueError('Invalid category ID')
        product = Product(product_data)
        MongoDBConnection.get_collection('products').insert_one(product.to_dict())
        return product

    @staticmethod
    def get_all(filters=None):
        if filters is None:
            filters = {}
        query = {}
        if 'name' in filters:
            query['name'] = {'$regex': filters['name'], '$options': 'i'}
        if 'category_id' in filters:
            query['category_id'] = filters['category_id']
        if 'min_price' in filters:
            query['price'] = {'$gte': float(filters['min_price'])}
        if 'max_price' in filters:
            query['price'] = query.get('price', {})
            query['price']['$lte'] = float(filters['max_price'])
        return list(MongoDBConnection.get_collection('products').find(query))

    @staticmethod
    def get_by_id(product_id):
        return MongoDBConnection.get_collection('products').find_one({'id': product_id})

    @staticmethod
    def update(product_id, data):
        if 'category_id' in data and data['category_id'] and not Category.get_by_id(data['category_id']):
            raise ValueError('Invalid category ID')
        return MongoDBConnection.get_collection('products').update_one(
            {'id': product_id},
            {'$set': data}
        )

    @staticmethod
    def delete(product_id):
        return MongoDBConnection.get_collection('products').delete_one({'id': product_id})