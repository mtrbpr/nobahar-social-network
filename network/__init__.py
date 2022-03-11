from rest_framework.permissions import BasePermission

BAD_REQUEST_BODY = {
    "error": {
        "enMessage": "Bad request!"
    }
}


class IsUserOwnerOfGroup(BasePermission):
    """
    Allows access only to group owner users.
    """

    def has_permission(self, request, view):
        return request.user.group and request.user.group.owner.id == request.user.id
