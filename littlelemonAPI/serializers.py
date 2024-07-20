
from rest_framework import  serializers
from django.contrib.auth.models import User ,Group 
from .models import *
from rest_framework.validators import UniqueValidator

class groupserializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields =('id','name')



class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','password')
    
class menuitemsserializer(serializers.ModelSerializer):
    
    class Meta:
        model = MenuItem
        fields =('id','category','tittle','price','featured')
        
        extra_kwargs = {
            'tittle' : { 'validators': [ UniqueValidator( queryset=MenuItem.objects.all() ) ] },
            'price': {'min_value': 5},
            
        } 

class cartoserializer(serializers.ModelSerializer):
    menuitem = menuitemsserializer(MenuItem)
    class Meta:
        model = cart
        fields =('id','quantity','unit_price','price','user','menuitem')
        
class orderitemserializer(serializers.ModelSerializer):
    class Meta:
        model= OrderItem
        fields =('id','quantity','unit_price','price','menuitem')        
        
class orderserializer(serializers.ModelSerializer):
    
    class Meta:
        model = order
        fields=('id','delivery_crew','user','status','total','date')    
        