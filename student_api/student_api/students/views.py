from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid
import json
from student_api.mongo_config import db
from bson import ObjectId

# Collections
students_collection = db.students

@csrf_exempt
def student_list(request):
    if request.method == 'GET':
        try:
            query = {}
            # Check query parameters first
            name = request.GET.get('name')
            age = request.GET.get('age')
            email = request.GET.get('email')
            student_id = request.GET.get('id')

            # If query parameters are not provided, check request body
            if request.body:
                try:
                    body_data = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)
                # Use body data only if query parameters are not provided
                if not name and 'name' in body_data:
                    name = body_data['name']
                if not age and 'age' in body_data:
                    age = body_data['age']
                if not email and 'email' in body_data:
                    email = body_data['email']
                if not student_id and 'id' in body_data:
                    student_id = body_data['id']

            # Build the query
            if name:
                query['name'] = {'$regex': f'^{name}$', '$options': 'i'}
            if age is not None:
                try:
                    query['age'] = int(age)
                except ValueError:
                    return JsonResponse({'error': 'Age must be a valid integer'}, status=400)
            if email:
                query['email'] = {'$regex': f'^{email}$', '$options': 'i'}
            if student_id:
                query['_id'] = {'$regex': f'^{student_id}$', '$options': 'i'}

            students = list(students_collection.find(query))
            for student in students:
                student['id'] = str(student.pop('_id'))
            return JsonResponse(students, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'POST':
        try:
            # Check query parameters first
            name = request.GET.get('name')
            age = request.GET.get('age')
            email = request.GET.get('email')

            # If query parameters are not provided, check request body
            if not (name and age and email) and request.body:
                try:
                    body_data = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)
                # Use body data only if query parameters are not provided
                if not name and 'name' in body_data:
                    name = body_data['name']
                if not age and 'age' in body_data:
                    age = body_data['age']
                if not email and 'email' in body_data:
                    email = body_data['email']

            # Validate required fields
            if not name or not age or not email:
                return JsonResponse({'error': 'Missing fields (name, age, email are required)'}, status=400)

            try:
                age = int(age)
            except ValueError:
                return JsonResponse({'error': 'Age must be a valid integer'}, status=400)

            student_id = str(uuid.uuid4())
            student = {
                '_id': student_id,
                'name': name,
                'age': age,
                'email': email
            }
            students_collection.insert_one(student)
            student['id'] = student.pop('_id')
            return JsonResponse(student, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            name = request.GET.get('name')
            age = request.GET.get('age')
            email = request.GET.get('email')
            student_id = request.GET.get('id')

            if name or age is not None or email:
                return JsonResponse({'error': 'DELETE only accepts id as a query parameter'}, status=400)

            if not student_id:
                return JsonResponse({'error': 'id query parameter is required to delete'}, status=400)

            result = students_collection.delete_one({'_id': {'$regex': f'^{student_id}$', '$options': 'i'}})
            if result.deleted_count > 0:
                return JsonResponse({'message': 'Student deleted'})
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def read_student(request, student_id):
    if request.method == 'GET':
        try:
            student = students_collection.find_one({'_id': {'$regex': f'^{student_id}$', '$options': 'i'}})
            if student:
                student['id'] = str(student.pop('_id'))
                return JsonResponse(student)
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['PUT', 'PATCH'])
def update_student(request):
    try:
        student_id = request.query_params.get('id')  # equivalent to request.GET

        if not student_id:
            return Response({'error': 'id is required in the query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        # Collect fields to update from query parameters
        update_fields = {}
        if 'name' in request.query_params:
            update_fields['name'] = request.query_params.get('name')
        if 'age' in request.query_params:
            try:
                update_fields['age'] = int(request.query_params.get('age'))
            except (ValueError, TypeError):
                return Response({'error': 'Age must be a valid integer'}, status=status.HTTP_400_BAD_REQUEST)
        if 'email' in request.query_params:
            update_fields['email'] = request.query_params.get('email')

        if not update_fields:
            return Response({'error': 'No valid fields to update'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the student in the database
        result = students_collection.update_one(
            {'_id': {'$regex': f'^{student_id}$', '$options': 'i'}},
            {'$set': update_fields}
        )

        if result.modified_count:
            return Response({'message': 'Student updated'}, status=status.HTTP_200_OK)
        return Response({'error': 'Student not found or no changes'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@csrf_exempt
def delete_student(request, student_id):
    if request.method == 'DELETE':
        try:
            result = students_collection.delete_one({'_id': {'$regex': f'^{student_id}$', '$options': 'i'}})
            if result.deleted_count:
                return JsonResponse({'message': 'Student deleted'})
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)