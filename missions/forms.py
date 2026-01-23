from django import forms
from .models import Mission, SubTask

class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ["title", "description", "deadline", "mission_type", "track"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "deadline": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "mission_type": forms.Select(attrs={"class": "form-select"}),
            "track": forms.Select(attrs={"class": "form-select"}),
        }

class SubTaskForm(forms.ModelForm):
    class Meta:
        model = SubTask
        fields = ["title", "xp_reward"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "xp_reward": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }