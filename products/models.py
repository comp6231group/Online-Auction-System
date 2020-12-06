from django.db import models

# Create your models here.
class Product(models.Model):
	productid = models.AutoField(primary_key=True, auto_created= True)
	userid = models.IntegerField(blank = True, null =True)
	winnerid = models.IntegerField(blank = True, null =True)
	productname = models.CharField(max_length=100)
	category = models.CharField(max_length=100)
	description = models.TextField()
	price = models.DecimalField(decimal_places=2,max_digits=7)
	quantity = models.IntegerField()
	image = models.ImageField(blank = True, null =True, upload_to='static/images/')
	endtime = models.DateTimeField(blank = True, null =True)
	highestbid = models.DecimalField(decimal_places=2,max_digits=7, null=True)
	