from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class category(models.Model):
    slug =models.SlugField(null=True)
    tittle =models.CharField(max_length=255,null=True)
    
    

    
class MenuItem(models.Model):
    category = models.ForeignKey(category,on_delete=models.PROTECT,null=True)
    tittle= models.CharField(max_length=255)
    price =models.DecimalField(decimal_places=2,max_digits=4)
    featured =models.BooleanField()
    
    
class cart(models.Model):
    user =models.ForeignKey(User,on_delete=models.CASCADE)
    menuitem =models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity =models.IntegerField()
    unit_price= models.DecimalField(max_digits=4,decimal_places=2)
    price= models.DecimalField(max_digits=5,decimal_places=2)
    
    class Meta:
        unique_together =('menuitem','user')


class order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='deliverycrew',null=True)
    status=models.BooleanField()
    total=models.DecimalField(max_digits=5,decimal_places=2)
    date =models.DateField()
     
     
class OrderItem(models.Model):
    order = models.ForeignKey(order,on_delete=models.CASCADE)
    menuitem=models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity=models.SmallIntegerField()
    unit_price= models.DecimalField(max_digits=4,decimal_places=2)
    price= models.DecimalField(max_digits=5,decimal_places=2)    
    
    class Meta:
        unique_together =('menuitem','order')