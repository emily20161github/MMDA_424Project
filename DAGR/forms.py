from django import forms

class UploadFileForm(forms.Form):
	file = forms.FileField()
	annotated_name = forms.CharField(max_length=200)
	keywords = forms.CharField(max_length=200)