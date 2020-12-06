from django import forms

from products.models import Product

class ProductForm(forms.ModelForm):
	class Meta:
		model = Product
		fields =[
			'userid',
			'productname',
			'category',
			'description',
			'price',
			'quantity',
			'image'
		]