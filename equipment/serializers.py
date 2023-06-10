from rest_framework import serializers
from .models import Equipment, BorrowHistory, ReturnHistory, EquipmentModification
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name']

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['createUser'] = instance.createUser.username
        return representation

class EquipmentIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id']

class ReturnHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnHistory
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['returnUser'] = instance.returnUser.username
        return representation

class BorrowHistorySerializer(serializers.ModelSerializer):
    returnHistorys = ReturnHistorySerializer(many=True, read_only=True)

    class Meta:
        model = BorrowHistory
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.username
        return representation

class EquipmentModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentModification
        fields = '__all__'