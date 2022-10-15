from rest_framework.serializers import ModelSerializer
from .models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    
    def save(self, *args, **kwargs):
        user = super(UserSerializer, self).save(*args, **kwargs)
        user.set_password(self.validated_data['password'])
        user.save()
