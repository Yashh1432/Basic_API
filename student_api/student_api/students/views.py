from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from student_api.mongo_config import db
from bson import ObjectId  # Import ObjectId to handle potential old data

# Collections
students_collection = db.students

@csrf_exempt
def student_list(request):
    if request.method == 'GET':
        try:
            query = {}
            name = request.GET.get('name')
            age = request.GET.get('age')
            email = request.GET.get('email')
            student_id = request.GET.get('id')

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
                query['_id'] = student_id

            students = list(students_collection.find(query))
            for student in students:
                # Convert _id to string if it's an ObjectId, then rename to id
                student['id'] = str(student.pop('_id'))
            return JsonResponse(students, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'POST':
        try:
            if not request.body:
                return JsonResponse({'error': 'Request body is empty'}, status=400)

            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

            name = data.get('name')
            age = data.get('age')
            email = data.get('email')

            if not name or not age or not email:
                return JsonResponse({'error': 'Missing fields (name, age, email are required)'}, status=400)

            try:
                age = int(age)
            except ValueError:
                return JsonResponse({'error': 'Age must be a valid integer'}, status=400)

            # Generate a UUID for _id
            student_id = str(uuid.uuid4())
            student = {
                '_id': student_id,  # Use UUID as _id
                'name': name,
                'age': age,
                'email': email
            }
            students_collection.insert_one(student)
            student['id'] = student.pop('_id')  # _id is already a string
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

            result = students_collection.delete_one({'_id': student_id})
            if result.deleted_count > 0:
                return JsonResponse({'message': 'Student deleted'})
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def read_student(request, student_id):
    if request.method == 'GET':
        try:
            student = students_collection.find_one({'_id': student_id})
            if student:
                student['id'] = str(student.pop('_id'))  # Convert _id to string
                return JsonResponse(student)
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def update_student(request, student_id):
    if request.method == 'PUT':
        try:
            if not request.body:
                return JsonResponse({'error': 'Request body is empty'}, status=400)

            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format in request body'}, status=400)

            update_fields = {k: v for k, v in data.items() if k in ['name', 'age', 'email']}
            if not update_fields:
                return JsonResponse({'error': 'No valid fields to update'}, status=400)

            if 'age' in update_fields:
                try:
                    update_fields['age'] = int(update_fields['age'])
                except ValueError:
                    return JsonResponse({'error': 'Age must be a valid integer'}, status=400)

            result = students_collection.update_one(
                {'_id': student_id},
                {'$set': update_fields}
            )
            if result.modified_count:
                return JsonResponse({'message': 'Student updated'})
            return JsonResponse({'error': 'Student not found or no changes'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_student(request, student_id):
    if request.method == 'DELETE':
        try:
            result = students_collection.delete_one({'_id': student_id})
            if result.deleted_count:
                return JsonResponse({'message': 'Student deleted'})
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
# ..................