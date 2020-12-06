from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from userprofiles.models import UserProfiles
from django.core.mail import send_mail
from products.models import Product
from .forms import ProductForm
from django.core.paginator import Paginator
from decimal import Decimal
import datetime
from background_task import background
from django.contrib.auth.models import User
from django.db.models import Q
import subprocess


# Create your views here.
def login_view(request,*args,**kwargs):
	request.session['userid']=""
	request.session['isadmin']=""
	context={
		"error_message":""
	}
	if request.method=="POST":
		user_email=request.POST.get('emailid')
		user_password=request.POST.get('password')
		get_user_details=UserProfiles.objects.filter(emailid=user_email, password=user_password)
		if len(get_user_details)!=0:
			get_user_details=UserProfiles.objects.get(emailid=user_email, password=user_password)
			request.session['userid'] = get_user_details.userid
			request.session['isadmin'] = get_user_details.isadmin
			request.session['username'] = get_user_details.firstname + " " + get_user_details.lastname
			return HttpResponseRedirect(reverse('home-view'))
		else:
			context={
				"error_message":"Invalid Email/Password"
			}
	return render(request,"login.html",context)


def home_view(request,*args,**kwargs):
	if request.session['userid']!="":		
		context={
			"username" : request.session['username']
		}
	else:
		return HttpResponseRedirect(reverse('login-view'))
	
	return render(request,"home.html",context)

def register_view(request,*args,**kwargs):
	context={
		"error_message":""
	}
	if request.method=="POST":
		user_firstname=request.POST.get('firstname')
		user_lastname=request.POST.get('lastname')
		user_email=request.POST.get('emailid')
		user_password=request.POST.get('password')
		get_user_details=UserProfiles.objects.filter(emailid=user_email)
		if len(get_user_details)==0:
			UserProfiles.objects.create(firstname=user_firstname,lastname=user_lastname,emailid=user_email, password=user_password)
			send_mail(
			    subject = "Registered successfully",
			    message = "You have successfully registered for Online Auction System",
			    from_email = "noreply@onlineauctionsystem.com",
			    recipient_list = [user_email,],
			)
			context={
				"error_message":"Registered successfully"
			}
		else:
			context={
				"error_message":"Email id already exists"
			}
	
	return render(request,"registeruser.html",context)


def upload_product_view(request,*args,**kwargs):
	print('offer item ',kwargs)
	form = ProductForm()
	if request.method == 'POST':
		form = ProductForm(request.POST or None,request.FILES)
		if form.is_valid():
			print('session userid ',request.session['userid'])
			form = form.save(commit=False)
			form.userid = request.session['userid']
			form.save()
			form = ProductForm()
			return HttpResponseRedirect(reverse('home-view'))

	context = {
		'form':form,
		"username" : request.session['username']
	}
	return render(request,"uploadproduct.html",context)


def products_list_view(request, *args, **kwargs):
	context={
		"username" : request.session['username']
	}
	all_products = Product.objects.all()
	print('pg no ',request.GET.get('page'))
	if request.GET.get('page') == None:
		page_number = 1
	else:
		page_number = request.GET.get('page')

	if request.GET.get('productid') != None:
		product_id = request.GET.get('productid')
		print('productid',product_id)
		return HttpResponseRedirect(reverse('product-view',kwargs={"productid": product_id}))

	paginator = Paginator(all_products, 6) # 8 items per page
	products = paginator.page(page_number)
	return render(request, 'viewlistings.html', {'products': products,'context': context})

def product_view(request, *args, **kwargs):
	context = {}
	if len(kwargs) != 0 :
		print(kwargs)
		product=Product.objects.get(productid=kwargs["productid"])
		print(request.session['isadmin'] )
		if product.endtime :
			bidtime = product.endtime
			bidtime  = str(bidtime)[:-6]
		else:
			bidtime = datetime.datetime.now()

		print('bidtime',bidtime)
		context={
			"productid" : kwargs["productid"],
			"product" : product,
			"isadmin" : request.session['isadmin'], 
			#"bidtime" : "Nov 17, 2020 15:45:25"
			#"bidtime" : "2020-11-17 15:47:17.012056"
			"bidtime" : bidtime,
			"username" : request.session['username']
		}
	print(request.POST.get('Option'))

	if request.POST.get('Option') != None :
		product=Product.objects.get(productid=request.POST.get("productid"))
		context ={
		"productid" : request.POST.get("productid"),
		"product" : product,
		"isadmin" : request.session['isadmin'],
		"username" : request.session['username']
		}

		if request.POST.get('Option') == 'start_bidding' :	
			product.endtime = datetime.datetime.now()+datetime.timedelta(minutes = 1)
			product.save()
			context["bidtime"] = product.endtime
			notify_users(product.productname)
			notify_or_restart(product.productid)
			subprocess.Popen("python manage.py process_tasks --sleep 60", shell=True)


		if request.POST.get('Option') == 'bid' :
			bid_price = request.POST.get("bid_price")
			if product.highestbid == None :
				if product.price < Decimal(bid_price) :
					product.highestbid = Decimal(bid_price)
					product.winnerid = request.session['userid']
					product.save()
					notify_change(product.productname, product.highestbid )
				else:
					context["error"] = "Bid amount should be greater than current highest bid price or base price"
			elif product.highestbid < Decimal(bid_price):
				product.highestbid = Decimal(bid_price)
				product.winnerid = request.session['userid']
				product.save()
				notify_change(product.productname, product.highestbid )
			else:
				context["error"] = "Bid amount should be greater than current highest bid price or base price"

			context["bidtime"] = str(product.endtime)[:-6]
			
	return render(request, 'viewproduct.html',context)


def purchases_view(request, *args, **kwargs):
	my_products = Product.objects.filter(winnerid = request.session["userid"])
	print('pg no ',request.GET.get('page'))
	if request.GET.get('page') == None:
		page_number = 1
	else:
		page_number = request.GET.get('page')

	if request.GET.get('productid') != None:
		product_id = request.GET.get('productid')
		print('productid',product_id)
		return HttpResponseRedirect(reverse('product-view',kwargs={"productid": product_id}))

	paginator = Paginator(my_products, 8) # 8 items per page
	products = paginator.page(page_number)
	return render(request, 'viewlistings.html', {'products': products})


def notify_users(productname):
	all_users = UserProfiles.objects.filter(isadmin = False);
	list_email = [d['emailid'] for d in all_users.values('emailid')] 
	print(list_email)
	# send_mail(
	#     subject = "Online Auction : Product is on sale, Hurry!",
	#     message = "Product is on sale :"+productname+"\nYou have 5 mins to bid until the auction ends.\n\nOnline Auction System",
	#     from_email = "noreply@onlineauctionsystem.com",
	#     recipient_list = list_email,
	# )

def notify_change(productname,bidprice):
	all_users = UserProfiles.objects.filter(isadmin = False);
	list_email = [d['emailid'] for d in all_users.values('emailid')] 
	print(list_email)
	# send_mail(
	#     subject = "Online Auction : Bidding is on, Hurry!",
	#     message = "Product is on sale :"+productname+"\nNew Bid Price: $"+str(bidprice)+"\nYou have 5 mins to bid until the auction ends.\n\nOnline Auction System",
	#     from_email = "noreply@onlineauctionsystem.com",
	#     recipient_list = list_email,
	# )


@background(schedule=60)
def notify_or_restart(productid):
	print(productid)
	product=Product.objects.get(productid=productid)
	print(product.productid)
	seller_user = UserProfiles.objects.get(userid=product.userid)
	if product.winnerid:
		winner_user = UserProfiles.objects.get(userid=product.winnerid)
		send_mail(
			    subject = "Auction Result : Congratulations - you have won !",
			    message = "You have have won "+product.productname+"\n\nOnline Auction System",
			    from_email = "noreply@onlineauctionsystem.com",
			    recipient_list = [winner_user.emailid,],
			)
		send_mail(
			    subject = "Auction Result - Your product is sold",
			    message = "Congratulations, your product is sold to "+winner_user.firstname +" "+winner_user.lastname +"\n\nOnline Auction System",
			    from_email = "noreply@onlineauctionsystem.com",
			    recipient_list = [seller_user.emailid,],
			)
	else:
		product.endtime = datetime.datetime.now()+datetime.timedelta(minutes = 1)
		product.save()
		notify_or_restart(product.productid)
		subprocess.Popen("python manage.py process_tasks --sleep 60", shell=True)
		

def logout_view(request,*args,**kwargs):
	request.session['userid']=""
	request.session['isadmin']=""
	return HttpResponseRedirect(reverse('login-view'))

def deregister_view(request,*args,**kwargs):
	context={
	"message":"",
	"btn_message":"",
	"url":""
	}
	user_offering=Product.objects.filter(userid = request.session["userid"])
	user_bidding=Product.objects.filter(winnerid = request.session["userid"])
	if len(user_offering)!=0 or len(user_bidding)!=0:
		context={
		"message":"You cannot de-register, there is an active product for sale or bidding!",
		"btn_message":"Return to Home",
		"url":"/home"
		}
	else:
		context={
		"message":"You have successfully de-registered!",
		"btn_message":"Return to Site",
		"url":"/"
		}
		UserProfiles.objects.get(userid = request.session["userid"]).delete()
		request.session['userid']=""
		request.session['isadmin']=""
	return render(request, 'deregister.html',context)
