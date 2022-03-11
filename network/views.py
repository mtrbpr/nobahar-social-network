import json

from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from network import BAD_REQUEST_BODY, IsUserOwnerOfGroup
from network.models import User, JoinRequest, ConnectionRequest, Group, ChatMessage
from network.serializers import UserSerializer, GroupSerializer, MyGroupSerializer, JoinRequestSerializer, \
    ConnectionRequestSerializer, ChatMessageSerializer


def _get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SignupAPIView(GenericAPIView):

    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user_instance = serializer.save()
                return Response(status=status.HTTP_200_OK, data={
                    'token': _get_tokens_for_user(user_instance)['access'],
                    "message": "successfull"
                })
            except IntegrityError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)


class LoginAPIView(GenericAPIView):

    def post(self, request):
        if ('email' not in request.data) or ('password' not in request.data):
            return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)
        try:
            user = User.objects.get(email=request.data['email'], password=request.data['password'])
            return Response(data={
                'token': _get_tokens_for_user(user)['access'],
                "message": "successfull"
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)


class GroupAPIViewSet(ModelViewSet):

    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(status=status.HTTP_200_OK, data={
              "group": {
                "id": str(instance.id)
              },
              "message": "successfull"
            })
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)

    @action(methods=['get'], url_path='my', detail=False, serializer_class=MyGroupSerializer)
    def my(self, request):
        if request.user.group:
            return Response(status=status.HTTP_200_OK, data={
                'group': self.get_serializer(instance=request.user.group).data
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)


class JoinRequestAPIViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = JoinRequestSerializer

    def create(self, request, *args, **kwargs):
        if request.user.group or ('groupId' not in request.data):
            return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)
        join_request = JoinRequest(user_id=request.user.id, group_id=request.data['groupId'])
        join_request.save()
        return Response(status=status.HTTP_200_OK, data={'message': 'successfull'})

    def list(self, request, *args, **kwargs):
        data = self.get_serializer(instance=request.user.join_requests.all(), many=True).data
        return Response(status=status.HTTP_200_OK, data={'joinRequests': data})

    @action(methods=['get'], url_path='group', detail=False)
    def group(self, request):
        if request.user.group:
            if request.user.group.owner.id == request.user.id:
                data = self.get_serializer(instance=request.user.group.join_requests.all(), many=True).data
                return Response(status=status.HTTP_200_OK, data={'joinRequests': data})
        return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)

    @action(methods=['post'], url_path='accept', detail=False)
    def accept(self, request):
        if request.user.group:
            if request.user.group.owner.id == request.user.id:
                if 'joinRequestId' in request.data:
                    try:
                        join_req = JoinRequest.objects.get(id=request.data['joinRequestId'])
                        if not join_req.user.group:
                            join_req.user.group = join_req.group
                            join_req.user.save()
                            return Response(status=status.HTTP_200_OK, data={'message': 'successfull'})
                    except JoinRequest.DoesNotExist:
                        pass

        return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)


class ConnectionRequestAPIViewSet(ModelViewSet):
    def create(self, request, *args, **kwargs):
        if request.user.group:
            if request.user.group.owner.id == request.user.id:
                if 'groupId' in request.data and Group.objects.filter(id=request.data['groupId']).exists():
                    connection_request = ConnectionRequest(requester=request.user.group,
                                                           requestee_id=request.data['groupId'])
                    connection_request.save()
                    return Response(status=status.HTTP_200_OK, data={'message': 'successfull'})

        return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)

    def list(self, request, *args, **kwargs):
        if request.user.group:
            if request.user.group.owner.id == request.user.id:
                return Response(status=status.HTTP_200_OK,
                                data={'requests': ConnectionRequestSerializer(
                                    instance=request.user.group.received_requests, many=True
                                ).data})
        return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)

    @action(methods=['post'], url_path='accept', detail=False)
    def accept(self, request):
        if request.user.group:
            if request.user.group.owner.id == request.user.id:
                if 'groupId' in request.data:
                    try:
                        con_req = ConnectionRequest.objects.get(requester_id=request.data['groupId'],
                                                                requestee_id=request.user.group.id,
                                                                accepted=False)
                        con_req.accepted = True
                        con_req.save()
                        return Response(status=status.HTTP_200_OK, data={'message': 'successfull'})
                    except ConnectionRequest.DoesNotExist:
                        pass

        return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)


@api_view(['POST', 'GET'])
def chat_view(request, user_id=None):
    user1 = request.user
    user2 = User.objects.get(id=user_id)
    if request.method == 'POST':
        group1 = request.user.group
        group2 = User.objects.get(id=user_id).group
        if are_groups_connected(group1, group2):
            cm = ChatMessage(user_from=request.user, user_to=User.objects.get(id=user_id),
                             message=request.data.get('message', ''))
            cm.save()
            return Response(status=status.HTTP_200_OK, data=json.dumps({"message": "successfull"}))
        return Response(status=status.HTTP_400_BAD_REQUEST, data=BAD_REQUEST_BODY)
    if request.method == 'GET' and user_id:
        cms = list(ChatMessage.objects.filter(Q(user_from_id=user1.id, user_to_id=user2.id) |
                                              Q(user_from_id=user2.id, user_to_id=user1.id))
                   .order_by('-id').all())
        data = ChatMessageSerializer(instance=cms, many=True).data
        return Response(status=status.HTTP_200_OK, data={
            'messages': data
        })


def are_groups_connected(group1, group2):
    if group1.id == group2.id:
        return True
    return ConnectionRequest.objects.filter(requester_id=group1.id, requestee_id=group2.id, accepted=True).exists()\
        or ConnectionRequest.objects.filter(requester_id=group2.id, requestee_id=group1.id, accepted=True).exists()


@api_view(['GET'])
def all_chats_view(request):
    user = request.user
    users1 = set(ChatMessage.objects.filter(Q(user_from_id=user.id) |
                                            Q(user_to_id=user.id)).values_list('user_from_id', flat=True).distinct())
    users2 = set(ChatMessage.objects.filter(Q(user_from_id=user.id) |
                                            Q(user_to_id=user.id)).values_list('user_to_id', flat=True).distinct())
    all_users = users1.union(users2)
    all_users.remove(user.id)

    return Response(status=status.HTTP_200_OK, data={
        'chats': [{
            'userId': u.id,
            'name': u.name
        } for u in User.objects.filter(id__in=all_users)]
    })

