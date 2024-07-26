from django.conf import settings
from django.contrib.auth import authenticate
from phonenumber_field.serializerfields import PhoneNumberField


from django.utils.translation import gettext_lazy as _


from rest_framework import serializers
from .models import User, Activation

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions


from rest_framework import status
from rest_framework.response import Response
from rest_framework import exceptions






class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = User
        fields = ["username","phone_number","email", "password", "password1"]

    def validate(self, attrs):
        
        if attrs.get("password") != attrs.get("password1"):
            raise serializers.ValidationError({"detail": "passswords doesnt match"})

        try:
            validate_password(attrs.get("password"))
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("password1", None)
        return User.objects.create_user(**validated_data)
    
class UserLoginSerialzer(serializers.Serializer):

    phone_number = PhoneNumberField(region=settings.PHONENUMBER_DEFAULT_REGION, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, style={'inpute_type':'password'})

    def _validat_phone_email(self, phone_number, email, password):
        user = None
        if email and password:
            user = authenticate(email=email, password=password)
        elif phone_number and password:
            user = authenticate(phone_number=phone_number, password=password)
        else:
            raise serializers.ValidationError(
                _("Enter your informations for login...")
            )        
        
        return user
    
    def validate(self, attrs):
        
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        user = self._validat_phone_email(email=email, phone_number=phone_number, password=password)

        if not user:
            raise exceptions.NotAuthenticated
        if not user.is_active :
            raise exceptions.MethodNotAllowed
        
        if not user.phone.is_veryfied:
            raise serializers.ValidationError(_('phone nymber is not veryfied'))
        

        attrs['user'] = user
        return attrs
    

# class ActivationSerializer(serializers.Serializer):
#     phone_number= PhoneNumberField()  

#     def validate_phone(self,)  


# class PhoneNumberSerializer(serializers.ModelSerializer):
#     phone_number = PhoneNumberField()

#     class Meta:
#         model= Activation
#         fields= ['phone_number']

#     def validate_phone(self, value):
#         try:
#             query = User.objects.get(phone__phone=value)
#             if query.phone.is_verified:
#                 message = _('phone number alredy is verified')
#                 raise serializers.ValidationError(message)
#         except User.DoesNotExist:
#             message = _('User dosent exist')
#             raise serializers.ValidationError(message)
#         return value    

class VerifyPhoneNumberSerializer(serializers.Serializer
                                  ):
    phone_number = PhoneNumberField()
    # code = serializers.CharField(max_length=50)

    # def validate_phone(self, value):
    #     query_set = User.objects.filter(user__phone_number=value)
    #     if query_set.exists():
    #         err_message = _('user not registered')
    #         raise serializers.ValidationError(err_message)
    #     return value


    
    def validate(self,validate_data):
        phone_number = validate_data.get('phone_number')
        security_code = validate_data.get('security_code')
        

        queryset = Activation.objects.create(phone_number=phone_number)
        queryset.send_confirmation()

        return validate_data










