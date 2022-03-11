from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from network.models import User, Group, JoinRequest, ConnectionRequest, ChatMessage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'password']
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True},
            'password': {'required': True, 'write_only': True},
        }

    def validate(self, attrs):
        if User.objects.filter(email=attrs.get('email', '')).exists():
            raise ValidationError()
        return attrs

    def create(self, validated_data):
        return super(UserSerializer, self).create(validated_data)


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    def validate(self, attrs):
        if self.context['request'].user.group:
            raise ValidationError()
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            group = Group(**validated_data)
            group.owner = self.context['request'].user
            group.save()
            user = self.context['request'].user
            user.group = group
            user.save()
            return group


class MyGroupSerializer(serializers.ModelSerializer):

    members = serializers.SerializerMethodField()

    def get_members(self, instance):
        return [{
            'id': mem.id,
            'name': mem.name,
            'email': mem.email,
            'rule': 'Owner' if mem.id == instance.owner.id else 'Normal'
        } for mem in instance.users.all()]

    class Meta:
        model = Group
        fields = ['name', 'description', 'members']
        read_only_fields = fields


class JoinRequestSerializer(serializers.ModelSerializer):

    groupId = serializers.IntegerField(source='group_id')
    userId = serializers.IntegerField(source='user_id')
    date = serializers.SerializerMethodField()

    def get_date(self, instance):
        return instance.date.timestamp()

    class Meta:
        model = JoinRequest
        fields = ['id', 'groupId', 'userId', 'date']
        read_only_fields = fields


class ConnectionRequestSerializer(serializers.ModelSerializer):
    connectionRequestId = serializers.IntegerField(source='id')
    groupId = serializers.IntegerField(source='requester_id')
    sent = serializers.SerializerMethodField()

    def get_sent(self, instance):
        return instance.date.timestamp()

    class Meta:
        model = ConnectionRequest
        fields = ['connectionRequestId', 'groupId', 'sent']
        read_only_fields = fields


class ChatMessageSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    sentby = serializers.SerializerMethodField()

    def get_date(self, instance):
        return instance.date.timestamp()

    def get_sentby(self, instance):
        return instance.user_from.id

    class Meta:
        model = ChatMessage
        fields = ['message', 'date', 'sentby']
        read_only_fields = fields
