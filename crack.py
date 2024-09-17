import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Attention
import numpy as np
from PIL import Image
import os

model = load_model('model/captcha_model.keras', custom_objects={'Attention': Attention})

def preprocess_image(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    img = img.resize((105, 30))  # 使用與訓練時相同的尺寸
    img_array = np.array(img) / 255.0  # 歸一化
    return np.expand_dims(img_array, axis=0)  # 添加批次維度


def decode_prediction(prediction):
    # 大寫+小寫+數字+填充符號
    char_map = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + 'abcdefghijklmnopqrstuvwxyz' + '0123456789' + '_'
    
    output = []
    for char_probs in prediction[0]:
        index = np.argmax(char_probs)
        char = char_map[index]
        if char != '_':  # 忽略填充字符
            output.append(char)
    
    return ''.join(output)

def predict_captcha(image_path):
    input_data = preprocess_image(image_path)
    prediction = model.predict(input_data)
    return decode_prediction(prediction)



if __name__ == "__main__":
    i=0
    j=0
    validation_path = 'datasets/validation'
    for file in os.listdir(validation_path):
        img_path=f'{validation_path}/{file}'
        result = predict_captcha(img_path)
        if(result==file.split('.')[0]):
            j+=1
        else:
            print(f'wrong predict:{result} , answer:{file.split('.')[0]}')
        i+=1
    print(f'accuracy:{j/i}')