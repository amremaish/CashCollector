from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    is_cash_collector = serializers.BooleanField()
    is_manager = serializers.BooleanField()
    is_frozen = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField(default=False, read_only=True)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken. Please choose another one.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance
