from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import UploadFileForm
from .models import PDF, ExtractedData

def upload(request):

    # Если POST-запрос, достаём из него файл
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            pdf = PDF.objects.upload(f)
            return HttpResponseRedirect('/extractor/{}/'.format(pdf.id))
    else:
        form = UploadFileForm()
    return render(request, 'extractor/upload.html', {'form': form})


def pdf(request, id):

    pdf = PDF.objects.get(id=id)
    datas = ExtractedData.objects.filter(pdf=pdf)
    form = UploadFileForm()

    return render(request, 'extractor/upload.html', locals())
