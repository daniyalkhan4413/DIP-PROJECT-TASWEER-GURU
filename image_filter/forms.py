from django import forms
from .models import UploadedImage, NumberPlateImage

FILTER_CHOICES = [
    ('gray', 'Grayscale'),
    ('blur', 'Blur'),
    ('canny', 'Edge Detection'),
    ('sepia', 'Sepia'),
    ('invert', 'Invert Colors'),
    ('sharpen', 'Sharpen'),
    ('threshold', 'Threshold / Binarize'),
    ('bright_contrast', 'Adjust Brightness/Contrast'),
    ('cartoon', 'Cartoonify'),
    ('sketch', 'Sketch Effect'),
    ('rotate', 'Rotate / Flip'),
]

class ImageUploadForm(forms.ModelForm):
    filter_type = forms.ChoiceField(choices=FILTER_CHOICES, label="Select Filter / Effect")

    class Meta:
        model = UploadedImage
        fields = ['image', 'filter_type']



class NumberPlateUploadForm(forms.ModelForm):
    class Meta:
        model = NumberPlateImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }