from django.db import models

# Create your models here.
class UserProfiles(models.Model):
	userid=models.AutoField(primary_key=True)
	firstname=models.CharField(max_length=100)
	lastname=models.CharField(max_length=100)
	emailid=models.CharField(max_length=100)
	password=models.CharField(max_length=100)
	isadmin=models.BooleanField(default=False)