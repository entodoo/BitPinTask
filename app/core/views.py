from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from . import serializers
from . import models
from .util.extend import StandardResultsSetPagination, RetrieveListViewSet
from .util.mixin import IsAuthenticatedPermission
from itertools import chain
from django.shortcuts import get_object_or_404


class RegistrationView(APIView):

    @swagger_auto_schema(
        operation_description="Users : all",
        operation_summary="ثبت ‌نام کاربر",
        security=[],
        request_body=serializers.RegistrationSerializer,
        responses={200: ''}
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.RegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
        return Response(status=200)


class RegisterRequestCodeView(generics.CreateAPIView):
    serializer_class = serializers.RegisterRequestCodeSerializer


class RegisterRequestCodeVerificationView(generics.CreateAPIView):
    serializer_class = serializers.RegisterRequestCodeVerificationSerializer


class ProfileView(IsAuthenticatedPermission, APIView):

    @swagger_auto_schema(
        operation_description="Users : authenticated users",
        operation_summary="ویرایش اطلاعات کاربر",
        request_body=serializers.UserSerializer,
        responses={200: ''})
    def patch(self, request, *args, **kwargs):
        instance = request.user
        serializer = serializers.UserSerializer(instance=instance, data=request.data, context={'request': request},
                                                partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Users : authenticated users",
        operation_summary="ویرایش اطلاعات کاربر",
        request_body=serializers.UserSerializer,
        responses={200: ''})
    def put(self, request, *args, **kwargs):
        instance = request.user
        serializer = serializers.UserSerializer(instance=instance, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: serializers.UserSerializer()})
    def get(self, request, *args, **kwargs):
        serializer = serializers.UserSerializer()
        instance = request.user
        return Response(serializer.to_representation(instance=instance), status.HTTP_200_OK)


class ResetPasswordRequestView(generics.CreateAPIView):
    serializer_class = serializers.ResetPasswordRequestSerializer


class ResetPasswordCheckCodeView(generics.CreateAPIView):
    serializer_class = serializers.ResetPasswordCheckCodeSerializer


class ResetPasswordView(generics.CreateAPIView):
    serializer_class = serializers.ResetPasswordSerializer


class ChangePasswordView(IsAuthenticatedPermission, APIView):

    def put(self, request, *args, **kwargs):
        user = self.request.user
        serializer = serializers.ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            if not user.check_password(old_password):
                return Response({"old_password": ["رمز عبور قبلی نادرست است"]},
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response({"details": 'رمز عبور با موفقیت تغییر کرد .'}, status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginRequestCodeView(generics.CreateAPIView):
    serializer_class = serializers.LoginRequestCodeSerializer


class LoginRequestCodeVerificationView(generics.CreateAPIView):
    serializer_class = serializers.LoginRequestCodeVerificationSerializer


class checkUserExistView(generics.CreateAPIView):
    serializer_class = serializers.checkUserSerializer


class ArticleViewSet(IsAuthenticatedPermission, RetrieveListViewSet):
    serializer_class = serializers.ArticleSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = models.Article.objects.all()
        return queryset
        

class PointView(IsAuthenticatedPermission, APIView):
    def post(self, request, article_id, *args, **kwargs):
        article = get_object_or_404(models.Article, pk=article_id)
        score = self.request.query_params.get('score', None)
        if score and 0 <= int(score)<=5:
            article.pointed(request, int(score))
            return Response(status.HTTP_200_OK)
        return Response({"score": 'یک عدد بین ۰ تا ۵ انتخاب کنید'}, status.HTTP_400_BAD_REQUEST)


