import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, LSTM, Dense, Reshape, BatchNormalization, Dropout, Attention, Flatten
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.utils import Sequence
from PIL import Image

#參數
TRAIN_DIR = 'datasets/training'
VAL_DIR = 'datasets/validation'
TEST_DIR = 'datasets/testing'
MODEL_DIR = 'model'
MODEL_PATH = 'model/captcha_model.keras'
IMG_HEIGHT = 30    
IMG_WIDTH = 105    
MAX_DIGITS = 6
num_classes = 26 + 26 + 10 + 1   # 大寫字母 + 小寫字母 + 數字 + 填充符號
BATCH_SIZE = 32
EPOCHS = 10


class CaptchaDataGenerator(Sequence):
    def __init__(self, directory, batch_size=32):
        # 初始化生成器，設置數據目錄和批次大小
        self.directory = directory
        self.batch_size = batch_size
        # 獲取所有 PNG 格式的文件名
        self.filenames = [f for f in os.listdir(directory) if f.endswith('.png')]
        # 計算總文件數
        self.n = len(self.filenames)

    def __len__(self):
        # 計算總批次數，向上取整以確保所有數據都被處理
        return int(np.ceil(self.n / float(self.batch_size)))

    def __getitem__(self, idx):
        # 獲取當前批次的文件名
        batch_filenames = self.filenames[idx * self.batch_size:(idx + 1) * self.batch_size]
        # 初始化批次的輸入數據 (圖像)
        batch_x = np.zeros((len(batch_filenames), IMG_HEIGHT, IMG_WIDTH, 3), dtype=np.float32)
        # 初始化批次的輸出數據 (標籤)
        batch_y = np.zeros((len(batch_filenames), MAX_DIGITS, num_classes), dtype=np.float32)

        for i, filename in enumerate(batch_filenames):
            # 讀取圖像
            img = Image.open(os.path.join(self.directory, filename))
            # 轉換為 RGB 格式
            img = img.convert('RGB')  
            # 調整圖像大小
            img = img.resize((IMG_WIDTH, IMG_HEIGHT))
            # 將圖像轉換為數組並歸一化
            img_array = np.array(img) / 255.0  
            batch_x[i] = img_array

            # 從文件名中提取標籤
            label = os.path.splitext(filename)[0]
            # 截斷或填充標籤至 MAX_DIGITS 長度
            label = label[:MAX_DIGITS].ljust(MAX_DIGITS, '_')

            for t, char in enumerate(label):
                # 如果超過 MAX_DIGITS，則停止處理
                if t >= MAX_DIGITS:
                    break
                if char == '_':
                    # 對於填充字符，設置最後一個類別為 1
                    batch_y[i, t, -1] = 1  
                else:
                    # 根據字符類型計算索引
                    if char.isupper():
                        index = ord(char) - ord('A')
                    elif char.islower():
                        index = ord(char) - ord('a') + 26
                    else:
                        index = ord(char) - ord('0') + 52
                    # 設置對應的類別為 1
                    batch_y[i, t, index] = 1

        # 返回處理後的批次數據
        return batch_x, batch_y


def create_model():
    # 輸入層
    inputs = Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3))
    
    #卷積層和池化層
    x = Conv2D(48, (3, 3), activation='relu', padding='same')(inputs)
    x = BatchNormalization()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    
    x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    
    x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    

    x = Flatten()(x)
    
    # 全連接層並重塑
    x = Dense(MAX_DIGITS * 128)(x)
    x = Reshape((MAX_DIGITS, 128))(x)
    
    # LSTM 層
    x = LSTM(128, return_sequences=True)(x)
    x = Dropout(0.25)(x)
    lstm_out = LSTM(128, return_sequences=True)(x)
    
    # 注意力機制
    attention = Attention()([lstm_out, lstm_out])
    

    outputs = Dense(num_classes, activation='softmax')(attention)
    

    model = Model(inputs=inputs, outputs=outputs)
    

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    return model


def main():

    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
        except RuntimeError as e:
            print(e)


    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)


    train_generator = CaptchaDataGenerator(TRAIN_DIR, batch_size=BATCH_SIZE)
    val_generator = CaptchaDataGenerator(VAL_DIR, batch_size=BATCH_SIZE)


    if os.path.exists(MODEL_PATH):
        print("Loading existing model...")
        model = load_model(MODEL_PATH, custom_objects={'Attention': Attention})
    else:
        print("Creating new model...")
        model = create_model()

    # 回調函數
    callbacks = [
        ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor='val_accuracy'),
        ReduceLROnPlateau(monitor='val_accuracy', factor=0.5, patience=3, min_lr=1e-7)
    ]

    # 訓練模型
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator,
        callbacks=callbacks
    )

    # 評估模型
    test_generator = CaptchaDataGenerator(TEST_DIR, batch_size=BATCH_SIZE)
    test_loss, test_accuracy = model.evaluate(test_generator)
    print(f"Test accuracy: {test_accuracy:.4f}")

if __name__ == "__main__":
    main()