from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .serializers import UserCreateSerializer, UserProfileSerializer


class UserCreateView(CreateAPIView):
    permission_classes = (IsAdminUser,)
    serializer_class = UserCreateSerializer


class UserProfileView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
