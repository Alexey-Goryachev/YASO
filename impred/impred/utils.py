import json
import numpy as np

import keras
from keras.models import Sequential
from keras.preprocessing.image import img_to_array, load_img
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping
from more_itertools import take

from .models import Images, NetModels, Labels

def get_netmodel_by_name(netmodel_name):
    model = NetModels.objects.get(name=netmodel_name)
    return model


def get_netmodel_by_id(netmodel_id):
    model = NetModels.objects.get(id=netmodel_id)
    return model


def get_image_by_id(image_id):
    image = Images.objects.get(id=image_id)
    return image


def get_labels(netmodel_id):
    labs = Labels.objects.extra(where=[f'netmodel_id={netmodel_id}']).order_by('predict_id').all()
    alab = []
    for lab in list(labs):
        # print(f'>> predict_id: {lab.predict_id}, name: {lab.name}')
        alab.append(lab.name)
    return alab


def get_label_by_name(netmodel_id, name):
    lab = Labels.objects.extra(where=[f"netmodel_id={netmodel_id} and name='{name}'"]).first()
    return lab


def get_labels_4choice(netmodel_id):
    labs = Labels.objects.extra(where=[f'netmodel_id={netmodel_id}']).order_by('predict_id').all()
    alab = []
    for lab in list(labs):
        # alab.append((lab.id, lab.name))
        alab.append((lab.name, lab.name))
    return alab


def get_labels_str(netmodel_id):
    alab = get_labels(netmodel_id)
    res = ", ".join(alab)
    return res


# Загрузка модели
def load_trained_model(model_path) -> Sequential:
    model = Sequential()
    model = keras.models.load_model(model_path) 
    return model


# Предсказание класса для изображения
def predict_class(model: Sequential, image_path: str):
    img = load_img(image_path, target_size=(64, 64))
    img_array = np.asarray([img_to_array(img)])

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)
    return predicted_class


def get_models(for_choise: bool = True):
    models = NetModels.objects.order_by('name').all()
    all_models = []
    if for_choise:
        for netm in models:
            y = (netm.pk, netm.name)
            all_models.append(y)
        # print(all_models)
        return all_models
    else:
        for netm in models:
            y = {"id": f"{netm.id}",
                 "name": netm.name,
                 "description": netm.description,
                 "version": netm.version,
                 "accuracy": "{:.2f}%".format(netm.accuracy * 100)
                }
            all_models.append(y)
        all_models = json.dumps(all_models)
        return all_models


def retrain_model(model: NetModels, image: Images):
    class_names = get_labels(model.pk)
    datagen = ImageDataGenerator(
                rotation_range=40,
                width_shift_range=0.2,
                height_shift_range=0.2,
                shear_range=0.2,
                zoom_range=0.2,
                horizontal_flip=True,
                fill_mode="nearest"
            )
    img = load_img(image.imagepath.path, target_size=(64, 64))
    x = np.asarray([img_to_array(img)])

    x4 = np.asarray([img_to_array(img)])
    for batch in take(5, datagen.flow(x, batch_size=1)):
        x4 = np.vstack((x4, batch))
    x4 = np.delete(x4, 0, 0)
    x4 = x4 / 255
    print(f">>> x_train.shape: {x4.shape}")

    t4 = class_names.index(image.real)
    t4 = np.zeros((5)) + t4
    t4 = to_categorical(t4, model.categories)
    print(f">>> y_train.shape: {t4.shape}")

    model3 = load_trained_model(model.modelpath.path)

    es_cb = EarlyStopping(monitor='val_accuracy', mode='max', patience=7, restore_best_weights=True)

    # Retraining the model
    history3 = model3.fit(x4, t4,
                            batch_size=128,
                            epochs=100,
                            validation_split=0.2,
                            callbacks=[es_cb])

    x4 = np.asarray([img_to_array(img)])
    x4 = x4 / 255
    y4 = model3.predict(x4)
    predicted_class = np.argmax(y4)
    label = class_names[predicted_class]
    print(f">>> Predict label: {label} (old: {image.predict.name})")

    # Save Retraining Model
    if label == image.real:
        print(f'Save Retraining Model {model.name}')
        model3.save(model.modelpath.path)

    return label
