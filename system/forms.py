from django import forms
from .models import GuestForeCast
from .models import StockItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class GuestForeCastForm(forms.ModelForm):
    class Meta:
        model = GuestForeCast
        fields = ['meal', 'shift', 'number_of_guests']

class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ['product_name', 'product_id', 'available_quantity', 'unit_of_measurement']

class CreateUserForm(UserCreationForm):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('chef', 'Chef'),
        ('audit', 'Audit'),
        ('accounts', 'Accounts Officer'),
        ('manager', 'Hospitality Manager'),
    ]

    first_name = forms.CharField(max_length=30, required=True, help_text='First name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last name')
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            role = self.cleaned_data['role']
            UserProfile.objects.create(user=user, role=role)
        return user

class EditUserForm(forms.ModelForm):
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    new_password = forms.CharField(required=False, widget=forms.PasswordInput, label="New Password")
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role']
    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        if self.user_instance:
            profile = self.user_instance.userprofile
            self.fields['role'].initial = profile.role
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('new_password'):
            user.set_password(self.cleaned_data['new_password'])
        if commit:
            user.save()
            profile = user.userprofile
            profile.role = self.cleaned_data['role']
            profile.save()
        return user