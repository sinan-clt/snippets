from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Snippet, Tag, User
from .serializers import SnippetSerializer, TagSerializer, UserSerializer, UserLoginSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework import serializers

class Register(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        mutable = request.POST._mutable
        request.POST._mutable = True
        request.POST['username'] = request.POST['email']
        request.POST._mutable = mutable
        serializer = UserSerializer(data=request.data)
        validate = serializer.is_valid()
        if validate is False:
            return Response({"status": 400, "message": "Incorrect Inputs", "data": serializer.errors})

        user = User.objects.create_user(name=request.POST['name'], mobile_number=request.POST['mobile_number'], username=request.POST['email'],
                                        email=request.POST['email'], password=request.POST['password'])
        user.is_active = True
        user.save()

        fields = ('id', 'username', 'email', 'mobile_number', 'name')
        data = UserSerializer(user, many=False, fields=fields)
        response = {
            'success': 'True',
            'status': 200,
            'message': 'User created successfully',
            'data': data.data,
        }

        return Response(response)



class UserLogin(APIView):
    permission_classes = [AllowAny]

    class Validation(serializers.Serializer):
        email = serializers.CharField()
        password = serializers.CharField()

    def post(self, request):

        validation = self.Validation(data=request.data)
        validate = validation.is_valid()
        if validate is False:
            return Response({"status": 400, "message": "Incorrect Inputs", "data": validation.errors})

        user = User.objects.filter(
            email=request.POST['email']).first()

        if user:
            mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['password'] = request.POST['password']
            request.POST._mutable = mutable
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            fields = ('id', 'username', 'email', 'phone_number', 'name')
            data = UserSerializer(user, many=False, fields=fields)
            response = {
                'success': 'True',
                'status': 200,
                'message': 'User logged in successfully',
                'token': serializer.data['token'],
                'data': data.data,
            }

            return Response(response)



class authenticatedUserDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = User.objects.filter(id=request.user.id)
        serializer = UserSerializer(items, many=True)
        return Response({'data':serializer.data,'status': 200, "message": "success"})



            
class OverviewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        snippet_count = Snippet.objects.count()
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)

        data = {
            'snippet_count': snippet_count,
            'snippets': serializer.data
        }

        return Response(data)


class CreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, snippet_id):
        try:
            snippet = Snippet.objects.get(id=snippet_id)
            serializer = SnippetSerializer(snippet)
            return Response(serializer.data)
        except Snippet.DoesNotExist:
            return Response({'error': 'Snippet not found'}, status=status.HTTP_404_NOT_FOUND)

# class UpdateAPI(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request, snippet_id):
#         try:
#             snippet = Snippet.objects.get(id=snippet_id)
#             serializer = SnippetSerializer(snippet, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Snippet.DoesNotExist:
#             return Response({'error': 'Snippet not found'}, status=status.HTTP_404_NOT_FOUND)

class UpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, snippet_id):
        try:
            snippet = Snippet.objects.get(id=snippet_id)
            serializer = SnippetSerializer(snippet, data=request.data)
            if serializer.is_valid():
                serializer.save()
                serialized_data = serializer.data
                tag_title = serialized_data.get('tag_title')
                if tag_title:
                    tag, _ = Tag.objects.get_or_create(title=tag_title)
                    serialized_data['tag'] = TagSerializer(tag).data
                return Response(serialized_data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Snippet.DoesNotExist:
            return Response({'error': 'Snippet not found'}, status=status.HTTP_404_NOT_FOUND)
            
        
class DeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, snippet_id):
        try:
            snippet = Snippet.objects.get(id=snippet_id)
            snippet.is_deleted = True
            snippet.save()
            remaining_snippets = Snippet.objects.filter(user=request.user, is_deleted=False)
            serializer = SnippetSerializer(remaining_snippets, many=True)
            data = {
                'message': "snippet deleted succesfully",
                'status':status.HTTP_200_OK,
                'snippets': serializer.data
            }
            return Response(data)

        except Snippet.DoesNotExist:
            return Response({'error': 'Snippet not found'}, status=status.HTTP_404_NOT_FOUND)

class TagListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

class TagDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, tag_id):
        try:
            tag = Tag.objects.get(id=tag_id)
            snippets = tag.snippet_set.all()
            serializer = SnippetSerializer(snippets, many=True)
            return Response(serializer.data)
        except Tag.DoesNotExist:
            return Response({'error': 'Tag not found'}, status=status.HTTP_404_NOT_FOUND)
