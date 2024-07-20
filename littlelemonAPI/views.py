from django.shortcuts import render
from rest_framework.decorators import api_view ,permission_classes
from django.contrib.auth.models import User, Group
from django.http import QueryDict
from rest_framework import generics
from . import serializers
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework.response import Response
from .serializers import userSerializer,menuitemsserializer ,cartoserializer 
from rest_framework.authtoken.models import Token
from .models import MenuItem ,category,cart ,order,OrderItem
from rest_framework.validators import UniqueValidator
from django.core.paginator import Paginator ,EmptyPage
from rest_framework.throttling import AnonRateThrottle,UserRateThrottle
from .throttles import *
from rest_framework.decorators import throttle_classes
# Create your views here.

  
                        ######################## Users Endpoint ###########################
    
@api_view(['GET'])                      # صح #get my data based on my token
@permission_classes([IsAuthenticated])
def get_user_data(request):
    user = request.user
    serializer = userSerializer(user)
    return Response(serializer.data)    
    
    
    
@api_view(['POST'])    
def users(request):                #create new user        ######working#######
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    user=User(
        username = username,
        email = email,
        password = password
    )
    user.save()
    saved ={'message':'saved'}
    return Response(saved)



                          ################### MENUITEMS ENDPOINTS ####################

@api_view(['GET','POST'])                              # to manipulate menu items list  #####working#####
@throttle_classes([AnonRateThrottle,UserRateThrottle])
def menuitems(request):
    if request.method =='GET':
        MENUitems = MenuItem.objects.all()
        
        price_filter= request.query_params.get('price')
        if price_filter:
            MENUitems =MENUitems.filter(price__lte=price_filter)
        featured_filter= request.query_params.get('featured')
        if featured_filter:
            MENUitems =MENUitems.filter(featured=featured_filter)    
        search_for = request.query_params.get('search')
        if search_for:
            MENUitems =MENUitems.filter(tittle__icontains=search_for)
        perpage = request.query_params.get('perpage',default=2)
        page = request.query_params.get('page',default=1)
        paginator = Paginator(MENUitems,per_page=perpage)
        try:
           MENUitems=paginator.page(number=page)
        except EmptyPage:
            MENUitems=[]    
        
        ser_items = menuitemsserializer(MENUitems, many=True)
        return Response(ser_items.data)
    
    
    elif request.method =='POST' :                               #data validation not working
        if IsAuthenticated():                                    #check authentication (manager)
            category_id = request.POST.get('categoryid')
            categoryvalue = category.objects.get(id=category_id)
            price = request.POST.get('price')           
            featured = request.POST.get('featured')
            tittle = request.POST.get('tittle')
            menuitem = MenuItem(
                category=categoryvalue,
                price = price,
                featured =featured,
                tittle = tittle,
            )
            menuitem.save()
            return Response('saved')
        else :
            return Response('denied access')
        
        
@api_view(['GET','POST','PUT','DELETE'])     
@throttle_classes([AnonRateThrottle,UserRateThrottle])  
def menuitem(request,pk) :                                      #get is working 
    if request.method == 'GET':
        menitem = MenuItem.objects.get(pk=pk)
        itemser = menuitemsserializer(menitem)    
        return Response(itemser.data)
    else :
        if IsAuthenticated:
            menitem = MenuItem.objects.get(pk=pk)
            if request.method == 'PUT':                                   #put --> updating whole record
                serializeditem =serializers.menuitemsserializer(menitem, cmp=request.data)
                
            elif request.method == 'PATCH':                               #partialy update --> field    
                serializeditem =serializers.menuitemsserializer(menitem, cmp=request.data,partial=True)
        
            elif request.method == 'DELETE':                              # delete record
                menitem.object.delete()  
                return Response({'message':'deleted'})  
            
            if serializeditem.is_valid():                                 #saving changes
                serializeditem.save()    
                return Response({'message':'altered'})
        
        else :
            return Response('u dont have access to do such thing')
        
                    
                    
                 ###################  USER GROUP MANAGMENT ENDPOINTS ####################                    
                 
                 
       
@api_view(['GET','POST','DELETE'])     
@throttle_classes([UserRateThrottle]) 
@permission_classes([IsAuthenticated])  
def managercontrol(request,pk=None):
    auth_header = request.META.get('HTTP_AUTHORIZATION')  # accessing header
    parts = auth_header.split()                           #put into array{list in py}
    token = parts[1]                                      #geting token
    userdata =Token.objects.get(key=token).user 
    
    if  userdata.groups.filter(name='manager').exists():                         # get only managers   # working 
        if request.method == 'GET':
            managers =User.objects.filter(is_superuser =True)
            managersser = userSerializer(managers)
            return Response(managersser.data)
        elif request.method == 'POST':                                  #put user into manager group
            user_id = request.POST.get('id')
            managergroup = Group.objects.get(name ='managers')
            if user_id:
                user = User.objects.get(id = user_id)
                managergroup.user_set.add(user)
                return Response({'message':'user now are manager'})
            else:
                return Response({'error': 'Missing user ID in request body.'})
    elif pk:
        if request.method =='DELETE' and userdata.groups.filter(name='manager').exists():                                 #delete user from manager group
            user = User.objects.get(id = pk) 
            if user:
                managergroup = Group.objects.get(name ='managers')
                user.groups.remove(managergroup)
    else :
        return Response({'error': 'u have no authority to take this action'})
    
    
@api_view(['GET','POST','DELETE'])     
@throttle_classes([UserRateThrottle]) 
@permission_classes([IsAuthenticated])  
def delv_crew_control(request,pk=None): 
    auth_header = request.META.get('HTTP_AUTHORIZATION')  # accessing header
    parts = auth_header.split()                           #put into array{list in py}
    token = parts[1]                                      #geting token
    userdata =Token.objects.get(key=token).user
    if userdata.groups.filter(name='manager').exists():
        if pk:
            if request.method == 'DELETE':
                user = User.objects.get(id = pk) 
                if user:
                    delv_crew = Group.objects.get(name ='delv crew')
                    user.groups.remove(delv_crew)
        
        else:    
            if request.method == 'GET':
                delv_crew_group = Group.objects.get(name='delv crew')  # Get the group object
                delv_crew = delv_crew_group.user_set.all()   
                if delv_crew:
                    crew_ser =userSerializer(delv_crew)
                    return Response(crew_ser.data)
            
            elif request.method == 'POST':
                user_id = request.POST.get('id')
                delvgroup = Group.objects.get(name ='delv crew')
                if user_id:
                    user = User.objects.get(id = user_id)
                    delvgroup.user_set.add(user)
                    return Response({'message':'user now are delivery crew'})    
    else :
        return Response({'message':'Access denied'})            
    
                 ###################  CART MANAGMENT ENDPOINTS ####################                    

     
@api_view(['GET','POST','DELETE'])     
@throttle_classes([UserRateThrottle]) 
@permission_classes([IsAuthenticated])
def Cart(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')  # accessing header
    parts = auth_header.split()                           #put into array{list in py}
    token = parts[1]                                      #geting token
    user =Token.objects.get(key=token).user               #user based on token
    cartitems = cart.objects.filter(user =user)
    
    if request.method == 'GET':                         #get working 
        cartserialize =cartoserializer(cartitems,many =True)
        return Response(cartserialize.data)
    
    elif request.method == 'POST':                      #post working
        menuitem_id = request.POST.get('menuitem')      
        userid =Token.objects.get(key=token).user_id
        price = request.POST.get('price')
        unit_price = request.POST.get('unitprice')
        quantity = request.POST.get('quantity')
        cartitem = cart(
            menuitem_id =menuitem_id,
            user_id =userid,
            price = price,
            unit_price=unit_price,
            quantity=quantity
        )
        cartitem.save()
        
        return Response({'':'saved'})
        
    elif request.method == 'DELETE':                    # delete working
        cartitems.object.delete()
        return Response({'message':'deleted'})
    
    
    
                 ###################  ORDER MANAGMENT ENDPOINTS #################### 
                 
from datetime import datetime 
@api_view(['GET','POST','DELETE','PATCH','PUT'])     
@throttle_classes([UserRateThrottle]) 
@permission_classes([IsAuthenticated])
def orders(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')  # accessing header
    parts = auth_header.split()                           #put into array{list in py}
    token = parts[1]                                      #geting token
    userdata =Token.objects.get(key=token).user
    user =Token.objects.get(key=token).user_id       # user id
    
    if request.method == 'GET':
        if userdata.groups.filter(name='managers').exists():   #check if user belong to managers group
            allorders = order.objects.all()
            all_ser = serializers.orderserializer(allorders,many =True)
            return Response({'at manager view test':all_ser.data})  
          
        if userdata.groups.filter(name='delv crew').exists():   #check if user belong to delv crew group
            emp_orders = order.objects.filter(delivery_crew_id=user)
            all_ser = serializers.orderserializer(emp_orders,many =True)
            return Response({'at delv crew view':all_ser.data})
        
        orders= order.objects.filter(user_id=user )             #if user normal customer
        orderser=serializers.orderserializer(orders,many=True)
        #man = orders[0].id              #لو عايز اعرض ORDERITEMS  هل اعمل لوب تمشي على كل اوردر في اللست
        return Response(orderser.data)  # ممكن يكون في اكتر من اوردر لشخص واحد 
    
    if request.method == 'POST':
        cartitems = cart.objects.get(user_id=user)
        total=0
        for i in cartitems:
            total =float(total+i.price)
        orderid = order.objects.create(status =0,total =total,date=datetime.now(),user_id=user).id # create order
        for item in cartitems:                      
            OrderItem.objects.create(quantity=item.quantity,unit_price=item.unit_price,price=item.price,menuitem_id=item.menuitem_id,order_id=orderid)    
           # create order items
        return Response({'message':'order created'})
    
    
@api_view(['GET','POST','DELETE','PATCH','PUT'])     
@throttle_classes([UserRateThrottle]) 
@permission_classes([IsAuthenticated])
def Order(request,pk):
    auth_header = request.META.get('HTTP_AUTHORIZATION')  # accessing header
    parts = auth_header.split()                           #put into array{list in py}
    token = parts[1]                                      #geting token
    userdata =Token.objects.get(key=token).user
    user =Token.objects.get(key=token).user_id 
    cust_order = order.objects.filter(id=pk)
    cusrtorder_id =cust_order[0].id
    if request.method == 'DELETE':
        if userdata.groups.filter(name='managers').exists():
            cust_order.delete()
            return Response({'message':'deleted'})
        
    if request.method=='GET':  
        if cust_order[0].user_id== user:                                # غالبا الاجابه اني استعمل get instead of filter هل اني افضل استخدم [0] صح ؟ 
            items = OrderItem.objects.filter(order_id=cusrtorder_id)
            itemsser=serializers.orderitemserializer(items,many =True)
            return Response(itemsser.data)
        else :
            return Response({'message':'denied'})
        
    if request.method=='PATCH':
        if userdata.groups.filter(name='delv crew').exists():                                            
            status = request.data.get('status')         #so he can only change status
            ser_item =serializers.orderitemserializer(cust_order,status) 
            
        if userdata.groups.filter(name='manager').exists():    
            ser_item =serializers.menuitemsserializer(cust_order, cmp=request.data,partial=True)
            
        if ser_item.is_valid():
                return Response({'message':'altered'})
    elif request.method == 'PUT':                       # هل المفروض احط بارشيال بترو علشان هو هيغير قيمتين بس؟
        if userdata.groups.filter(name='manager').exists():    
            ser_item =serializers.menuitemsserializer(cust_order, cmp=request.data,partial =True)
            return Response({'message':'altered'})
                
    