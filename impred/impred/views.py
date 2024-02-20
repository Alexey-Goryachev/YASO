from django.shortcuts import render, redirect
# from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

import numpy as np
from PIL import Image
# import tensorflow as tf 
import keras
from keras.models import Sequential
from keras.preprocessing.image import img_to_array, load_img

from .forms import ImageForm, NetModelForm, LabelForm
from .models import Images, NetModels, Labels
# from .model_cifar10 import predict_image
from .utils import get_netmodel_by_name, get_labels, get_labels_str


netmodel_name = "SIFAR-10"

# Загрузка модели
def load_trained_model(model_path) -> Sequential:
    model = Sequential()
    model = keras.models.load_model(model_path) 
    return model


# Предсказание класса для изображения
def predict_class(model, image_path):
    # img = Image.open(image_path)
    # img = img.resize((64, 64))  # Замените на размеры, на которых была обучена модель
    img = load_img(image_path, target_size=(64, 64))
    img_array = np.asarray([img_to_array(img)])

    # img_array = np.expand_dims(np.array(img) / 255.0, axis=0)  # Нормализация изображения
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
            netmodel = get_netmodel_by_name(netmodel_name)
            model = load_trained_model(netmodel.modelpath.path)
            class_names = get_labels(netmodel.id)

            image_path = new_image.imagepath.path
            predicted_class = predict_class(model, image_path)
            label = class_names[predicted_class]
            predict = Labels.objects.filter(name=label).filter(netmodel=netmodel).first()

            # Привязка к модели и предсказанию
            new_image.predict = predict
            new_image.save()
            return redirect('impred:predictimage')
    else:
        form = ImageForm()
    return render(request, 'impred/loadimage.html', context={'image_form': form})


def predictimage(request):
    # Получение id новой картинки из сессии
    new_image_id = request.session.get("new_image_id")

    if new_image_id:
        # Фильтрация изображений по новому id
        images = Images.objects.filter(id=new_image_id)
        # Удаление new_image_id из сессии
        del request.session["new_image_id"]
    else:
        images = Images.objects.all()
    return render(request, 'impred/predictimage.html', context={'images': images})


def netmodels(request):
    net_models = NetModels.objects.order_by('name').all()
    # print(f">>> netmodels = {net_models}")
    net_labels = []
    for nm in net_models:
        net_labels.append({"netmodel": nm, "labels": get_labels_str(nm.id)})
    # print(f">>> netmodels: {net_labels}")
    return render(request, 'impred/netmodels.html', context={'netmodels': net_labels})


@login_required
def netmodel(request, netmodel_id):
    if request.method == 'POST':
        form = NetModelForm(request.POST, request.FILES)

        if form.is_valid():
            new_model = form.save(commit=False)
            new_model.save()
            return redirect('impred:netmodels')
    else:
        if netmodel_id:
            netmodel = NetModels.objects.get(id=netmodel_id)
            form = NetModelForm(netmodel, instance=NetModels)
        else:
            form = NetModelForm()
    return render(request, 'impred/netmodel.html', context={'form': form})


# def labels(request, netmodel_id):
#     if netmodel_id:
#         labs = Labels.objects.filter(netmodel_id=netmodel_id).all()
#     else:
#         labs = Labels.objects.all()
#     return render(request, 'impred/netmodels.html', context={'labels': labs})


# @login_required
# def label(request, netmodel_id):
#     if request.method == 'POST':
#         form = LabelForm(request.POST)

#         if form.is_valid():
#             new_label = form.save(commit=False)
#             new_label.save()
#             return redirect('impred:labels')
#     else:
#         form = LabelForm()
#     return render(request, 'impred/label.html', context={'form': form})
