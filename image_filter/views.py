from django.shortcuts import render, redirect
from .forms import ImageUploadForm, NumberPlateUploadForm
from .models import NumberPlateImage
from .utils import apply_filter
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .utils import process_image
import os, base64, io



import cv2



from django.http import StreamingHttpResponse, HttpResponse













def home(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()

            input_path = obj.image.path
            output_path = os.path.join(settings.MEDIA_ROOT, 'processed', os.path.basename(input_path))
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            apply_filter(input_path, form.cleaned_data['filter_type'], output_path)
            obj.processed_image = 'processed/' + os.path.basename(input_path)
            obj.save()

            return render(request, 'result.html', {'obj': obj})
    else:
        form = ImageUploadForm()
    return render(request, 'home.html', {'form': form})








@csrf_exempt
def process_image_view(request):
    # expects multipart/form-data with 'image' blob and numeric params
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')

    file = request.FILES.get('image')
    if not file:
        return HttpResponseBadRequest('Image file required')

    try:
        brightness = float(request.POST.get('brightness', 0))
        contrast = float(request.POST.get('contrast', 100))
        blur = int(request.POST.get('blur', 0))
        sharpen = int(request.POST.get('sharpen', 0))
        threshold = int(request.POST.get('threshold', 0))
    except Exception as e:
        return HttpResponseBadRequest('Bad parameters: ' + str(e))

    # Save temporary input
    tmp_in = os.path.join(settings.MEDIA_ROOT, 'temp', f'input_{request.session.session_key or "anon"}.png')
    os.makedirs(os.path.dirname(tmp_in), exist_ok=True)
    with open(tmp_in, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    # Process
    tmp_out = os.path.join(settings.MEDIA_ROOT, 'temp', f'out_{request.session.session_key or "anon"}.png')
    os.makedirs(os.path.dirname(tmp_out), exist_ok=True)

    detected = process_image(tmp_in, tmp_out,
                             brightness=brightness,
                             contrast=contrast,
                             blur=blur,
                             sharpen=sharpen,
                             threshold=threshold)

    # return base64 string of processed image and optionally detected info
    with open(tmp_out, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    b64url = 'data:image/png;base64,' + b64

    return JsonResponse({'processed_image_base64': b64url, 'detected': detected})






def landingpage(request):
    return render(request,template_name='lander.html')