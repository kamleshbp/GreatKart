from django import forms
from .models import Account


class RegistrationForm(forms.ModelForm):


    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    class Meta:

        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number']
    

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            
            self.fields[field].widget.attrs['class'] = 'form-control'
            placeholder = field.replace('_', ' ').title()
            self.fields[field].widget.attrs['placeholder'] = f'Enter {placeholder}'

    def clean(self):

        cleaned_data = super().clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']

        if password != confirm_password:
            raise forms.ValidationError('Password does not match!')

        return cleaned_data