from django.db import models

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    processed_image = models.ImageField(upload_to='processed/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)



class NumberPlateImage(models.Model):
    image = models.ImageField(upload_to='plates/')
    processed_image = models.ImageField(upload_to='plates/processed/', null=True, blank=True)
    detected_plates = models.TextField(blank=True)  # store recognized plate numbers as CSV or JSON
    created_at = models.DateTimeField(auto_now_add=True)