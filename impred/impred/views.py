from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .forms import ImageForm, NetModelForm, LabelForm
from .models import Images, NetModels, Labels
from .utils import get_labels_str, get_netmodel_by_name
from .model_cifar10 import predict_image


# Create your views here.
def main(request):
    return render(request, 'impred/index.html', context={'title': "Завантажте свою світлину і я спробую вгадати, що на ній зображено."})


def loadimage(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            new_image = form.save(commit=False)
            #new_image.user = request.user  # предварительно для будущего usera
            new_image.save()

            # Сохранение id новой картинки в сессии
            request.session["new_image_id"] = new_image.id

            # # Предварительно код для анализа images моделью и привязки к классу.
            image_path = new_image.imagepath.path
            # prediction = model_function(image_path)  # предварительно функция для предсказания класса
            # # Получение или создание соответствующей метки (label)
            # label, created = Labels.objects.get_or_create(name=prediction, netmodel=new_image.netmodel)
            label = predict_image(image_path)

            netmodel_name = "SIFAR-10"
            netmodel = get_netmodel_by_name(netmodel_name)            
            predict = Labels.objects.filter(name=label).filter(netmodel=netmodel).first()
            # # Привязка к модели и предсказанию
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
def netmodel(request, netmodel_id=None):
    if request.method == 'POST':
        form = NetModelForm(request.POST, request.FILES)
        req = request.POST.dict()

        if form.is_valid():
            new_model = form.save(commit=False)
            new_model.save()

            label_str = str(req['labels'])
            if label_str:
                label_str = label_str.replace(' ', '').split(',')
                num = 0
                for lb_name in label_str:
                    label, *_ = Labels.objects.get_or_create(name=lb_name, predict_id=num, netmodel=new_model)
                    num += 1

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
