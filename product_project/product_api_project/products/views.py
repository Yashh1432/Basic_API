from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ProductListView(APIView):
    def get(self, request):
        try:
            filters = {
                'name': request.query_params.get('name', ''),
                'category_id': request.query_params.get('category_id', ''),
                'min_price': request.query_params.get('min_price', ''),
                'max_price': request.query_params.get('max_price', '')
            }
            filters = {k: v for k, v in filters.items() if v}
            logger.debug(f"GET filters: {filters}")
            products = Product.get_all(filters)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in ProductListView.get: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = {
                'name': request.query_params.get('name', ''),
                'price': float(request.query_params.get('price', 0.0)) if request.query_params.get('price') else 0.0,
                'category_id': request.query_params.get('category_id', ''),
                'description': request.query_params.get('description', '')
            }
            logger.debug(f"POST data: {data}")
            serializer = ProductSerializer(data=data)
            if serializer.is_valid():
                product = serializer.save()
                return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in ProductListView.post: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductDetailView(APIView):
    def get(self, request):
        try:
            product_id = request.query_params.get('id')
            if not product_id:
                return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            logger.debug(f"GET product_id: {product_id}")
            product = Product.get_by_id(product_id)
            if not product:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in ProductDetailView.get: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            product_id = request.query_params.get('id')
            if not product_id:
                return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            product = Product.get_by_id(product_id)
            if not product:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            data = {
                'name': request.query_params.get('name', product['name']),
                'price': float(request.query_params.get('price', product['price'])) if request.query_params.get('price') else product['price'],
                'category_id': request.query_params.get('category_id', product['category_id']),
                'description': request.query_params.get('description', product['description'])
            }
            logger.debug(f"PUT data: {data}")
            serializer = ProductSerializer(product, data=data, partial=True)
            if serializer.is_valid():
                updated_product = serializer.save()
                return Response(ProductSerializer(updated_product).data)
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in ProductDetailView.put: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            product_id = request.query_params.get('id')
            if not product_id:
                return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            logger.debug(f"DELETE product_id: {product_id}")
            product = Product.get_by_id(product_id)
            if not product:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            Product.delete(product_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error in ProductDetailView.delete: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)