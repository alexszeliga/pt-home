from django import forms
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    # email = forms.EmailField(required=True) # Example of adding an extra field

    # class Meta(UserCreationForm.Meta):
    #     fields = UserCreationForm.Meta.fields + ('email',)
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
