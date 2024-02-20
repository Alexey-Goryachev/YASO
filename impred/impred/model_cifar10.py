import numpy as np

import keras
from keras.models import Sequential
from keras.preprocessing.image import img_to_array, load_img

from ds_project.settings import BASE_DIR
from .utils import get_netmodel_by_name, get_labels

netmodel_name = "SIFAR-10"

# Defining array. Each item of array represent integer value of labels. 10 item for 10 integer label
# class_names = ['Airplane', 'Automobile', 'Bird', 'Cat', 'Deer', 'Dog', 'Frog', 'Horse', 'Ship', 'Truck']
netmodel = get_netmodel_by_name(netmodel_name)
model3 = Sequential()
# model3 = keras.models.load_model(f"{BASE_DIR}/data/model-cifar10.h5")
print(f">>> modelpath: {netmodel.modelpath.path}")
model3 = keras.models.load_model(netmodel.modelpath.path)
class_names = get_labels(netmodel.id)

def predict_image(image_path: str) -> str:
    # img = load_img(f"{BASE_DIR}/media/images/Красава.jpg", target_size=(64, 64))
    img = load_img(image_path, target_size=(64, 64))
    X_test2 = np.asarray([img_to_array(img)])
    X_test2 = X_test2.astype('float32') / 255
    y_hat3 = model3.predict(X_test2)
    predict_index = np.argmax(y_hat3[0])
    result = class_names[predict_index]
    return result
