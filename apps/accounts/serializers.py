from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        return token
        
    def validate(self, attrs):
        data = super().validate(attrs)
        data['id'] = str(self.user.id)
        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['is_staff'] = self.user.is_staff
        data['is_superuser'] = self.user.is_superuser
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'middle_name', 
                  'birth_date', 'gender', 'city', 'phone_number', 
                  'whatsapp_number', 'photo', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'is_staff', 'is_superuser']
        extra_kwargs = {
            'photo': {'required': False}
        }

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'phone_number']
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'middle_name', 
                 'birth_date', 'gender', 'city', 'phone_number', 
                 'whatsapp_number', 'photo']
        read_only_fields = ['id']
        
class WhatsAppUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['whatsapp_number']
        
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']
        read_only_fields = ['id']
        
class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'is_staff', 'is_superuser']
        read_only_fields = ['id']
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user 