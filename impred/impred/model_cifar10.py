import numpy as np

import keras
from keras.models import Sequential
from keras.preprocessing.image import img_to_array, load_img

from ds_project.settings import BASE_DIR


model3 = Sequential()
model3 = keras.models.load_model(f"{BASE_DIR}/data/model-cifar10.h5")

# Defining array. Each item of array represent integer value of labels. 10 item for 10 integer label
class_names = ['Airplane', 'Automobile', 'Bird', 'Cat', 'Deer', 'Dog', 'Frog', 'Horse', 'Ship', 'Truck']

def predict_image(image_path: str) -> str:
    # img = load_img(f"{BASE_DIR}/media/images/Красава.jpg", target_size=(64, 64))
    img = load_img(image_path, target_size=(64, 64))
    X_test2 = np.asarray([img_to_array(img)])
    X_test2 = X_test2.astype('float32') / 255
    y_hat3 = model3.predict(X_test2)
    predict_index = np.argmax(y_hat3[0])
    result = class_names[predict_index]
    return result
