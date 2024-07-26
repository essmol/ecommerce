from django.conf import settings
from django.urls import reverse
from django.contrib import redirects
from django.utils.translation import gettext_lazy as _



from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import RedirectView
from django.http import HttpResponseRedirect

from rest_framework.response import Response
from rest_framework import status


from dj_rest_auth.views import LoginView, LogoutView
from dj_rest_auth.registration.views import RegisterView, SocialLoginView


from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView


import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

from .models import User, Activation
from .serializers import (
    RegistrationSerializer, 
    UserLoginSerialzer,
    VerifyPhoneNumberSerializer,

)

# Create your views here.

class RegistertionView(GenericAPIView):

    
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            username= serializer.validated_data['username']
            email = serializer.validated_data["email"]
            phone_number = serializer.validated_data['phone_number']
            data = {"phone_number": phone_number,"username": username, }
            user_obj = get_object_or_404(User, email=email, phone_number=phone_number)
            
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# class LoginEmailView(APIView):

#     def get(self, request, token, *args, **kwargs):
#         try:
#             token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])  
#             user_id = token.get['user_id']
#         except  ExpiredSignatureError:
#             return Response(
#                 {'detail': _('token was expierd')},
#                 status.HTTP_400_BAD_REQUEST
#             )    
#         except InvalidSignatureError:
#             return Response(
#                 {'detail':_('token is invalid')}

#             )
#         user = User.objects.get(pk=user_id)

#         if user.is_active:
#             return Response('you active already your account')
#         user.is_active== True
#         user.save()

#         return Response(
#             {'detail': _('your account have been verified and activated successfully')}
#         )    

class UserLoginView(LoginView):

    serializer_class =  UserLoginSerialzer


class UserLogout(LogoutView):
    pass    


class SendResendView(GenericAPIView):
    serializer_class = VerifyPhoneNumberSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  
        return      
    
class ActivationView(APIView):

    

    # url = 'users:registeration'

    def post(self, request, *args, **kwargs):
        phone_number=request.data.get('phone_number')
        
        user = User.objects.filter(phone__phone_number=phone_number).first()
        
        query_set = Activation.objects.filter(
            phone_number=phone_number, is_verified=False
        ).first()
        print(query_set)
        # if not query_set.phone:
        #     message = {"detail": _("User dosent exist.")}
        #     return Response(message, status=status.HTTP_400_BAD_REQUEST)
        # query_set.send_confirmation()

        message = {'detail':_('Activation Code send to {phone_number} ')}
        return Response(message, status.HTTP_200_OK)  



        
