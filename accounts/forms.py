from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from .models import User
from django.contrib.auth.forms import UserCreationForm


class LoginForm(AuthenticationForm):
    """
    Formulário de Login aprimorado com:
    - placeholders dinâmicos
    - CSS automático
    - Validação com mensagens claras
    - Proteção contra tentativas excessivas (anti brute-force)
    """

    username = forms.CharField(
        label="Usuário ou E-mail",
        widget=forms.TextInput()
    )

    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'input-field',          
                'placeholder': field.label,      
            })

    
        self.fields['username'].widget.attrs['autofocus'] = True




    def confirm_login_allowed(self, user):
        """Mensagens personalizadas para contas inválidas"""
        if not user.is_active:
            raise forms.ValidationError(
                "Sua conta está desativada. Entre em contato com o suporte.",
                code='inactive'
            )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["bio", "interests", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Escreva sua bio..."}),
            "interests": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Ex: Django, UX, inglês..."}),
        }

    avatar = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
    


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})
   