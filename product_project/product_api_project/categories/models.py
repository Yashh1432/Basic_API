from pymongo import MongoClient
import uuid

class MongoDBConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = MongoClient('mongodb://localhost:27017/product_db')
            cls._instance.db = cls._instance.client['product_db']
        return cls._instance

    @classmethod
    def get_collection(cls, collection_name):
        return cls().__getattribute__('db')[collection_name]

class Category:
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.id = str(data.get('id', uuid.uuid4()))
        self.name = data.get('name', '')
        self.description = data.get('description', '')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    @staticmethod
    def create(category_data):
        category = Category(category_data)
        MongoDBConnection.get_collection('categories').insert_one(category.to_dict())
        return category

    @staticmethod
    def get_all(filters=None):
        if filters is None:
            filters = {}
        query = {}
        if 'name' in filters:
            query['name'] = {'$regex': filters['name'], '$options': 'i'}
        return list(MongoDBConnection.get_collection('categories').find(query))

    @staticmethod
    def get_by_id(category_id):
        return MongoDBConnection.get_collection('categories').find_one({'id': category_id})

    @staticmethod
    def update(category_id, data):
        return MongoDBConnection.get_collection('categories').update_one(
            {'id': category_id},
            {'$set': data}
        )

    @staticmethod
    def delete(category_id):
        return MongoDBConnection.get_collection('categories').delete_one({'id': category_id})