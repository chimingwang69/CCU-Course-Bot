import shutil
import os
import random

work_path = os.getcwd()
data_path = work_path + r'\download'  #原始資料
training_data_path = work_path + r'\datasets\training'  
testing_data_path = work_path + r'\datasets\testing'    
validation_data_path = work_path + r'\datasets\validation'  


def make_datasets():  
    '''
    validation  :  testing  :  training   
        1       :     1     :     8
    隨機分配,有些要特別丟進training的可以先抓起來
    '''
    files = os.listdir(data_path)
    n = int(len(files) / 10)

    # 建立validation datasets
    for i in range(n):
        f = random.choice(files)
        shutil.move(os.path.join(data_path, f), os.path.join(validation_data_path, f))
        files = os.listdir(data_path)

    # 建立testing datasets
    files = os.listdir(data_path)
    for i in range(n):
        f = random.choice(files)
        shutil.move(os.path.join(data_path, f), os.path.join(testing_data_path, f))
        files = os.listdir(data_path)

    # 建立training datasets
    files = os.listdir(data_path)
    for f in files:
        shutil.move(os.path.join(data_path, f), os.path.join(training_data_path, f))


def clean_datasets():
    '''
    清空  
    \datasets\training  
    \datasets\testing  
    \datasets\validation  
    '''
    if input('輸入y來刪除檔案')== 'y':
        shutil.rmtree(training_data_path)
        shutil.rmtree(testing_data_path)
        shutil.rmtree(validation_data_path)
        os.mkdir(training_data_path,777)
        os.mkdir(testing_data_path,777)
        os.mkdir(validation_data_path,777)
        print('刪除成功')
    else:
        print('未刪除')


action=input('輸入m建立datasets,輸入c清空datasets')
if action == 'm':
    make_datasets()
elif action == 'c':
    clean_datasets()
else:
    print('啥都沒幹')