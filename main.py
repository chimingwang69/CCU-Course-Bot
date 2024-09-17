################################# ///***WARNING***\\\ #################################
#僅用來練習selemium等網頁爬蟲工具與LSTM+CNN模型識別驗證碼
#若因其他衍生用途造成一切責任一律與本人無涉
################################# \\\***WARNING***/// #################################
import time
import re
import crack
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
################################# ///***config***\\\ #################################
# 學號
id = ''
# 密碼
passwd = ''
# 科目代碼
course_id = '7505009'
# 班別
class_no = '01'
# 學分
credit = ''
# 系所
dept = 'I001'
# 年級
grade = '1'
# 第幾頁
page = '2'
# 分類
cate = '2'
subcate = '2'

data = {'dept': dept, 'grade': grade, 'cge_cate': cate, 'cge_subcate': subcate, 'SelectTag': '1', 'page': page}
data['course'] = course_id+'_'+class_no
data[course_id+'_'+class_no] = credit

#User-Agent
useragent = 'Mozilla/5.0 (X11; Linux; en-US; rv:127.0) Gecko/20160210 Firefox/127.0'
headers = {'User-Agent': useragent}

#selenium options
options = Options()
options.add_argument("--headless=new")

#url
check_url = 'http://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi'
login_url = 'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/login.php'

# 是否第一次登入
first_time_login = True
################################# \\\***config***/// #################################

def final_check(session_id):
    '''
    檢查課程是否加選成功
    若有返回True,無則返回False
    input session_id (type: str)
    return True/False (type: bool)
    '''
    driver = webdriver.Edge(options = options)
    url=(f'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Selected_View00.cgi?session_id={session_id}')
    try:
        driver.get(url)
        if re.search(course_id, driver.page_source):
            print('加選成功')
            return True
        else:
            print('尚未選上')
            return False
    except Exception as e:
        print(f'發生錯誤：{e}')
        return False
    finally:
        driver.quit()


def check_available(session_id):
    '''
    檢查課程是否在加選頁面內
    若不在返回False
    input session_id (type: str)
    return True/False (type: bool)
    '''
    driver = webdriver.Edge(options = options)
    url=f'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi?session_id={session_id}&use_cge_new_cate=1&m=0&dept={dept}&grade={grade}&page={page}&cge_cate={cate}&cge_subcate={subcate}'
    try:
        driver.get(url)
        if re.search(course_id, driver.page_source):
            print('找到課程')
            driver.quit()
            return True
        else:
            print('未找到課程請檢查設定')
            driver.quit()
            return False
    except Exception as e:
        print(f'發生錯誤：{e}')
        return False
    finally:
        driver.quit()
        
def login(id,passwd):
    '''
    登入選課系統並取得session_id用來後續選課
    :input id (type: str)
    :input passwd (type: str)
    :param session_id (type: str) : 登入階段的token
    :return session_id (type: str) or None
    '''
    try:
        session_id='1'
        driver = webdriver.Edge(options = options)
        while len(session_id)!=36:
            driver.get(login_url)
            driver.find_element(By.ID, 'captchaImage').screenshot(f'captcha.png')
            captcha = crack.predict_captcha('captcha.png')
            driver.find_element(By.ID, 'id').send_keys(id)
            driver.find_element(By.ID, 'password').send_keys(passwd)
            driver.find_element(By.ID, 'captcha_input').send_keys(captcha)
            time.sleep(0.5)
            driver.find_element(By.ID, 'submit_botton').click()
            try:
                if re.search('密碼有誤', driver.page_source):
                    print('登入失敗 請檢查帳號密碼')
                    return None
                match = re.search(r'session_id=([A-Za-z0-9]+)', driver.page_source)
                if match:
                    session_id = match.group(1)
                    print(f"登入成功 本次session_id: {session_id}")
                    return session_id
            except:
                continue
    finally:
        driver.quit()
        


while True:
    # 掛一個try...expect來避免奇怪的狀況
    try:
        session_id=login(id, passwd)
        # 帳密錯登入失敗就break
        if session_id is None:
            break
        data['session_id'] = session_id
        # 第一次run先檢查課程是否存在與衝堂
        if first_time_login:
            if not check_available(session_id):
                break    
            res = requests.Session().post(check_url, data=data, headers=headers).content.decode('UTF-8')
            if re.search('衝堂', res):
                print(res)
                break
        first_time_login = False
        # 每加選180次重新登入取得新session_id
        for i in range(0,180):
            res = requests.Session().post(check_url, data=data, headers=headers).content.decode('UTF-8')
        # 最後檢查是否有加選上
        if final_check(session_id):
            break
    except:
        continue
    
    
