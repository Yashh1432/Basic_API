from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import CategorySerializer
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CategoryListView(APIView):
    def get(self, request):
        try:
            filters = {'name': request.query_params.get('name', '')}
            filters = {k: v for k, v in filters.items() if v}
            logger.debug(f"GET filters: {filters}")
            categories = Category.get_all(filters)
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in CategoryListView.get: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = {
                'name': request.query_params.get('name', ''),
                'description': request.query_params.get('description', '')
            }
            logger.debug(f"POST data: {data}")
            serializer = CategorySerializer(data=data)
            if serializer.is_valid():
                category = serializer.save()
                return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in CategoryListView.post: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryDetailView(APIView):
    def get(self, request):
        try:
            category_id = request.query_params.get('id')
            if not category_id:
                return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            logger.debug(f"GET category_id: {category_id}")
            category = Category.get_by_id(category_id)
            if not category:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in CategoryDetailView.get: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            category_id = request.query_params.get('id')
            if not category_id:
                return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            category = Category.get_by_id(category_id)
            if not category:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
            data = {
                'name': request.query_params.get('name', category['name']),
                'description': request.query_params.get('description', category['description'])
            }
            logger.debug(f"PUT data: {data}")
            serializer = CategorySerializer(category, data=data, partial=True)
            if serializer.is_valid():
                updated_category = serializer.save()
                return Response(CategorySerializer(updated_category).data)
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in CategoryDetailView.put: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            category_id = request.query_params.get('id')
            if not category_id:
                return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            logger.debug(f"DELETE category_id: {category_id}")
            category = Category.get_by_id(category_id)
            if not category:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
            Category.delete(category_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error in CategoryDetailView.delete: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)