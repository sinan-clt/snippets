from rest_framework import serializers
from .models import Tag, Snippet, User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(UserSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
    class Meta:
        model=User
        fields = ('id','username','email','mobile_number','name','password')


class UserLoginSerializer(serializers.Serializer):

    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password is not found.'
            )
        try:
           refresh = RefreshToken.for_user(user)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email and password does not exists'
            )
        return {
            'email':user.email,
            'token': str(refresh.access_token),
            'access': str(refresh)
        }



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'title']



class SnippetSerializer(serializers.ModelSerializer):
    tag_title = serializers.CharField(write_only=True)
    tag = TagSerializer(read_only=True)

    class Meta:
        model = Snippet
        fields = ['id', 'title', 'content', 'timestamp', 'tag', 'tag_title']
    
    def create(self, validated_data):
        tag_title = validated_data.pop('tag_title')
        tag, _ = Tag.objects.get_or_create(title=tag_title)
        validated_data['tag'] = tag
        return super().create(validated_data)

    def update(self, instance, validated_data):
        tag_title = validated_data.pop('tag_title')
        tag, _ = Tag.objects.get_or_create(title=tag_title)
        instance.tag = tag
        return super().update(instance, validated_data)