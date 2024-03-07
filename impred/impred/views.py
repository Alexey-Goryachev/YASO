import os

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import ImageForm, NetModelForm, PredictImageForm
from .models import Images, NetModels, Labels
from .utils import get_labels_str, get_labels,load_trained_model, predict_class, get_models, get_netmodel_by_id, get_image_by_id, get_labels_4choice, retrain_model


netmodel_name = "SIFAR-10"

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

            # Предварительно код для анализа images моделью и привязки к классу.
            netmodel_id = request.POST['listmodels']
            netmodel = get_netmodel_by_id(netmodel_id)
            model = load_trained_model(netmodel.modelpath.path)
            class_names = get_labels(netmodel.id)

            image_path = new_image.imagepath.path
            predicted_class = predict_class(model, image_path)
            label = class_names[predicted_class]
            predict = Labels.objects.filter(name=label).filter(netmodel=netmodel).first()

            # Привязка к модели и предсказанию
            new_image.netmodel = netmodel
            new_image.predict = predict
            new_image.save()
            return redirect('impred:predictimage', id=new_image.id)
    else:
        form = ImageForm()
        models = get_models(for_choise=False)
    return render(request, 'impred/loadimage.html', context={'image_form': form, 'models': models})


def predictimage(request, id: int = None):
    image_id = id
    print(f'>>> image_id = {image_id}')

    print(f'>>> request.method = {request.method}')
    if request.method == 'POST':                    # Реализация метода PATCH
        req = request.POST.dict()
        form = PredictImageForm(request.POST)
        image = get_image_by_id(image_id)
        real = form.fields['real']
        real.choices = get_labels_4choice(image.netmodel.id)
        # print(f'>>> real.choices: {real.choices}')
        
        if form.is_valid():
            image.name = req.get('name')
            image.real = req.get('real')
            image.save()
            return redirect('impred:predictimages')
        else:
            print(f'>>> Form invalid! {form.errors}')
            
    if image_id:
        image = get_image_by_id(image_id)
        form = PredictImageForm(instance=image)
        return render(request, 'impred/predictimage.html', context={'form': form, 'image': image})
    
    return redirect('impred:predictimages')


# def predictimage_view(request):
#     new_image_id = request.session.get("new_image_id")  # Получение id новой картинки из сессии
#     print(f'>>> new_image_id = {new_image_id}')

#     if new_image_id is not None:
#         del request.session["new_image_id"]             # Удаление new_image_id из сессии
#         predictimage(request, new_image_id)

#     return redirect('impred:predictimages')


@login_required
def predictimage_del(request, id: int):
    image = Images.objects.filter(id=id).first()
    image_path = image.imagepath.path
    # print(f'>>> Delete image: {id}')
    # image.delete()
    img_del = Images.objects.filter(id=id).delete()
    # print(f'>>> Delete file: {image_path}')
    try:
        os.remove(image_path)
        print(f'>>> Delete image: Ok')
    except Exception as err:
        message = str(err)
        image.save()
        messages.error(request, message)
        print(f'>>> Delete image: Error: {message}')
    return redirect('impred:predictimages')

def predictimages(request):
    images = Images.objects.all()
    return render(request, 'impred/predictimages.html', context={'images': images})


def netmodels(request):
    net_models = NetModels.objects.order_by('name').all()
    net_labels = []
    for nm in net_models:
        net_labels.append({"netmodel": nm, "labels": get_labels_str(nm.id)})
    return render(request, 'impred/netmodels.html', context={'netmodels': net_labels})


@login_required
def netmodel(request, id=None):
    netmodel_id = id
    if request.method == 'POST':
        form = NetModelForm(request.POST, request.FILES)
        req = request.POST.dict()

        if form.is_valid():
            new_model = form.save(commit=False)
            new_model.save()

            labels = str(req['labels'])
            if label_str:
                label_str = labels.replace(' ', '').split(',')
                label_tmp = list(set(label_str))
                if len(label_str) != len(label_tmp):
                    form.add_error('labels', f'The list of labels contains non-unique names!')
                elif len(label_str) != new_model.categories:
                    form.add_error('labels', f'The number of labels {len(label_str)} does not correspond to the number of categories {new_model.categories}!')
                else:
                    num = 0
                    for lb_name in label_str:
                        label, *_ = Labels.objects.get_or_create(name=lb_name, predict_id=num, netmodel=new_model)
                        num += 1
                    return redirect('impred:netmodels')

            elif new_model.categories > 0:
                form.add_error('labels', 'Labels required!')

        head = request.session.get("head")
        return render(request, 'impred/netmodel.html', context={'form': form, 'labels': labels, 'head': head})
        # return redirect('impred:netmodels')
    else:
        if netmodel_id:
            netmodel = NetModels.objects.get(id=netmodel_id)
            form = NetModelForm(instance=netmodel)
            labels = get_labels_str(netmodel_id)
            head = 'Edit NetModel'
            request.session["head"] = head
        else:
            form = NetModelForm()
            labels = ''
            head = 'Load new NetModel'
            request.session["head"] = head

    # print(f'>>> labels: {form.labels}')
    return render(request, 'impred/netmodel.html', context={'form': form, 'labels': labels, 'head': head})


@login_required
def netmodel_del(request, netmodel_id):
    model = NetModels.objects.filter(id=netmodel_id).first()
    model_path = model.modelpath.path
    print(f'>>> Delete file: {model_path}')
    os.remove(model_path)
    print(f'>>> Delete model: {id}')
    model.delete()
    print(f'>>> Delete model: Ok')
    return redirect('impred:netmodels')


@login_required
def retrainmodel(request, image_id):
    image = get_image_by_id(image_id)
    model = get_netmodel_by_id(image.netmodel.pk)
    label = retrain_model(model, image)

    if label == image.real:
        predict = Labels.objects.filter(name=label).filter(netmodel=model).first()
        # Привязка к предсказанию
        image.predict = predict
        image.save()
        responce_data = {"ok": True, "label": label, "message": "Additional training of the model was completed successfully"}
    else:
        responce_data = {"ok": False, "label": label, "message": f"After additional training, the model was unable to correctly identify the picture ({label})"}
    return JsonResponse(responce_data)
