from django import forms

#form fields for getting IP address, username and password of the Grid Master
class lbdn(forms.Form):
	IP_Address = forms.CharField(label="Grid Master IP Address/FQDN" , max_length = 15)
	username = forms.CharField(label="Grid Master Username", max_length = 100)
	password = forms.CharField(label="Grid Master Password", widget = forms.PasswordInput())
