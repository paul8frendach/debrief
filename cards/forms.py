from django import forms
from django.forms import inlineformset_factory
from .models import Card, Argument, Source


class CardForm(forms.ModelForm):
    """Form for creating and editing cards"""
    class Meta:
        model = Card
        fields = ['scope', 'topic', 'subcategory', 'title', 'stance', 'hypothesis', 'conclusion', 'visibility']
        widgets = {
            'scope': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Border Security'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card title'}),
            'stance': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Supports, Opposes, Neutral'}),
            'hypothesis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your hypothesis or thesis statement'}),
            'conclusion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your conclusion'}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
        }


class ArgumentForm(forms.ModelForm):
    """Form for creating and editing arguments"""
    class Meta:
        model = Argument
        fields = ['type', 'summary', 'detail', 'order']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Argument summary'}),
            'detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Additional details (optional)'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
        }


class SourceForm(forms.ModelForm):
    """Form for adding sources to arguments"""
    class Meta:
        model = Source
        fields = ['title', 'url', 'author', 'publication_date', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Source title'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author name (optional)'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes (optional)'}),
        }


# Formset for creating multiple arguments at once
ArgumentFormSet = inlineformset_factory(
    Card,
    Argument,
    form=ArgumentForm,
    extra=2,
    can_delete=True
)