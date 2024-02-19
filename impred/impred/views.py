from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import ImageForm
from .models import Images, NetModels, Labels
from .model_cifar10 import predict_image
import tensorflow as tf 
from PIL import Image
import numpy as np


# Загрузка модели
def load_trained_model(model_path):
    return tf.keras.models.load_model(model_path)


# Предсказание класса для изображения
def predict_class(model, image_path):
    img = Image.open(image_path)
    img = img.resize((64, 64))  # Замените на размеры, на которых была обучена модель
    img_array = np.expand_dims(np.array(img) / 255.0, axis=0)  # Нормализация изображения
    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)
    return predicted_class


# Create your views here.
def main(request):
    return render(request, 'impred/index.html', context={'title': "Завантажте свою світлину і я спробую вгадати, що на ній зображено."})


def loadimage(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            new_image = form.save(commit=False)
            # new_image.user = request.user  # предварительно для будущего usera
            new_image.save()

            # Сохранение id новой картинки в сессии
            request.session["new_image_id"] = new_image.id

            # # Предварительно код для анализа images моделью и привязки к классу.
            model_path = "./data/model-cifar10.h5"
            model = load_trained_model(model_path)
            image_path = new_image.imagepath.path
            predicted_class = predict_class(model, image_path)

            #Получение или создание соответствующей метки (label)
            if new_image.netmodel:
                label, created = Labels.objects.get_or_create(predict_id=predicted_class, netmodel=new_image.netmodel)
                # # Привязка к модели и предсказанию
                new_image.predict = label
                new_image.save()
                return redirect('impred:predictimage')
            else:
                return HttpResponse("Ошибка: netmodel не может быть None")
    else:
        form = ImageForm()
    return render(request, 'impred/loadimage.html', context={'image_form': form})


def predictimage(request):

    # Получение id новой картинки из сессии
    new_image_id = request.session.get("new_image_id")

    # Фильтрация изображений по новому id
    images = Images.objects.filter(id=new_image_id)
    #images = Images.objects.all()

    # Удаление new_image_id из сессии
    del request.session["new_image_id"]
    return render(request, 'impred/predictimage.html', context={'images': images})
