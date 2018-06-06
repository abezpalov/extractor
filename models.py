import io
import os
import uuid
import fitz
import json
from PIL import Image

from django.conf import settings

from django.db import models

class PDFManager(models.Manager):

    def upload(self, f):

        pdf = PDF()
        pdf.title = f.name
        pdf.save()

        # TODO Установить проверку на соответствеие pdf
        # *.pdf, *.xps, *.oxps, *.cbz, *.fb2 or *.epub
        if f.name.endswith('.pdf'):
            # Сохраняем PDF-файл
            pdf.file.save('{}/{}'.format(pdf.id, f.name), f)
            pdf.save()
            os.chmod(pdf.filename, 0o755)

        elif f.name.endswith('.xps') or f.name.endswith('.cbz') or f.name.endswith('.fb2') \
            or f.name.endswith('.oxps') or f.name.endswith('.epub'):

            # Сохраняем временный файл
            # Создаём запись в базе
            data = ExtractedData(pdf=pdf)
            data.title = f.name

            # Сохраняем исходный файл
            data.file.save('{}/{}'.format(pdf.id, data.title), f)
            data.save()
            os.chmod(data.filename, 0o755)

            # Открываем временный файл
            if f.name.endswith('.xps') or f.name.endswith('.cbz') or f.name.endswith('.fb2'):
                filename = '{}/{}.pdf'.format(pdf.id, f.name[:-4])
                pdf.title = '{}.pdf'.format(pdf.title[:-4])
            elif f.name.endswith('.oxps') or f.name.endswith('.epub'):
                filename = '{}/{}.pdf'.format(pdf.id, f.name[:-5])
                pdf.title = '{}.pdf'.format(pdf.title[:-5])


            doc = fitz.open(data.filename)
            pdfbytes = doc.convertToPDF()
            f = io.BytesIO()
            f.write(pdfbytes)
            pdf.file.save(filename, f) # TODO
            pdf.save()
            os.chmod(pdf.filename, 0o755)


        # TODO Извлекаем данные
        pdf.extract_meta()
        pdf.extract_text()
        pdf.extract_links()
        pdf.extract_preview()
        pdf.extract_imgs()

        return pdf

class PDF(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=256, null=True, blank=True, default=None)
    file = models.FileField(upload_to='extractor/', max_length=1024, null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    def __str__(self):
        return self.title

    def _filename(self):
        return os.path.join(settings.MEDIA_ROOT, self.file.name)

    filename = property(_filename)

    objects = PDFManager()

    def extract_meta(self):

        # Открываем PDF и извлекаем метаданные
        doc = fitz.open(self.filename)
        metadata = json.dumps(doc.metadata)
        f = io.StringIO()
        f.write(metadata)

        # Создаём запись в базе
        data = ExtractedData(pdf=self)
        data.title = 'metadata.json'

        # Сохраняем файл
        data.file.save('{}/{}'.format(self.id, data.title), f)
        data.save()

        # Устанавливаем права доступа к файлу
        os.chmod(data.filename, 0o755)

    def extract_text(self):

        # Открываем PDF и извлекаем текст
        doc = fitz.open(self.filename)
        text = ''

        for n in range(doc.pageCount):
            page = doc.loadPage(n)
            text = '{}\n{}'.format(text, page.getText('text'))

        f = io.StringIO()
        f.write(text)

        # Создаём запись в базе
        data = ExtractedData(pdf=self)
        data.title = 'text.txt'

        # Сохраняем файл
        data.file.save('{}/{}'.format(self.id, data.title), f)
        data.save()

        # Устанавливаем права доступа к файлу
        os.chmod(data.filename, 0o755)

    def extract_links(self):

        # Открываем PDF и извлекаем ссылки
        doc = fitz.open(self.filename)
        links = set()

        for n in range(doc.pageCount):
            page = doc.loadPage(n)
            for link in page.getLinks():
                try:
                    link = link['uri']
                except KeyError:
                    continue
                links.add(link)
        links = '\n'.join(links)

        f = io.StringIO()
        f.write(links)

        # Создаём запись в базе
        data = ExtractedData(pdf=self)
        data.title = 'links.txt'

        # Сохраняем файл
        data.file.save('{}/{}'.format(self.id, data.title), f)
        data.save()

        # Устанавливаем права доступа к файлу
        os.chmod(data.filename, 0o755)

    def extract_preview(self):

        # Открываем первую страницу PDF
        doc = fitz.open(self.filename)
        page = doc.loadPage(0)

        # Создаём запись в базе
        data = ExtractedData(pdf=self)
        data.title = 'preview.png'
        data.file = 'extractor/{}/{}'.format(self.id, data.title)

        # Сохраняем файл
        pix = page.getPixmap(alpha=False)
        pix.writePNG(data.filename)
        data.save()

        # Устанавливаем права доступа к файлу
        os.chmod(data.filename, 0o755)

    def extract_imgs(self):

        # Открываем PDF и проходим по каждой странице
        doc = fitz.open(self.filename)
        for n in range(doc.pageCount):
            page = doc.loadPage(n)
            imgs = page.getImageList()
            for i in imgs:
                pix = fitz.Pixmap(doc, i[0])
                if str(pix.colorspace) == 'fitz.Colorspace(fitz.CS_CMYK) - DeviceCMYK':
                    colorspace = 'CMYK'
                elif str(pix.colorspace) == 'fitz.Colorspace(fitz.CS_GRAY) - DeviceGray':
                    colorspace = 'GRAY'
                elif str(pix.colorspace) == 'fitz.Colorspace(fitz.CS_RGB) - DeviceRGB':
                    colorspace = 'RGB'

                # Создаём запись в базе
                data = ExtractedData(pdf=self)
                data.title = 'img-{}.png'.format(i[0])
                data.file = 'extractor/{}/{}'.format(self.id, data.title)

                # Сохраняем файл
                img = Image.frombytes(colorspace, [pix.width, pix.height], pix.samples)
                img = img.convert('RGB')
                img.save(data.filename, 'png')
                data.save()

                # Устанавливаем права доступа к файлу
                os.chmod(data.filename, 0o755)






    class Meta:
        ordering = ['created']

class ExtractedData(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pdf = models.ForeignKey('PDF', on_delete=models.CASCADE)
    title = models.CharField(max_length=256, null=True, blank=True, default=None)
    file = models.FileField(upload_to='extractor/', max_length=1024, null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    def __str__(self):
        return self.title

    def _filename(self):
        return os.path.join(settings.MEDIA_ROOT, self.file.name)

    filename = property(_filename)

    class Meta:
        ordering = ['created']
