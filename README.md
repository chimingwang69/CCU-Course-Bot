# CCU搶課腳本

> [!WARNING]
> 本腳本僅用來訓練驗證碼辨識模型，結合Selenium所衍生如加選、設定不當造成選課系統癱瘓等後果
> 而發生包括但不限於帳號被鎖、課不見、癱瘓系統遭依中華民國刑法§360起訴，本人一概不承擔任何責任

## 1. Description

該修的通識修完了就來分享吧，明年畢業後不會再更新

以前自己是套[Pytesseract](https://pypi.org/project/pytesseract/)庫來辨識驗證碼，accuracy也不太高，改隨機5或6碼後更是大幅降低

於是自己空閒時間train了一個LSTM+CNN(沒有CTC)的模型，直接上登入頁面實戰accuracy大概0.95

失敗的有再丟回去訓練，如果你覺得我的模型有待改進，歡迎直接取用我的datasets

以後改google recaptcha這個專案就廢了

## 2. Requirement

| 套件       | 版本                           |
| ---------- | ------------------------------ |
| Numpy      |                                |
| Pillow     |                                |
| Request    |                                |
| Selenium   | >4.0.0  使用conda的請注意版本 |
| Tensorflow | >2.0.0                         |

## 3. Usage

1. [ ] 確認裝好上面required package
2. [ ] main.py內config區塊填好資料
3. [ ] 確認terminal目錄為當前資料夾(e.g. 在資料夾右鍵以code開啟)

enjoy~

config不會填?

去加選頁面找到課程後，右鍵打開框架原始碼

以台灣的植物那頁為例會看到:

```html
<input type=hidden name='session_id' value='祕密'>
<input type='hidden' name='dept' value='I001'>
<input type='hidden' name='grade' value='1'>
<INPUT type='hidden' name='cge_cate' value='2'>
<INPUT type='hidden' name='cge_subcate' value='2'>
<input type='hidden' name='page' value='2'>
<INPUT TYPE='hidden' name='e' value='0'>
<INPUT TYPE='hidden' name='m' value='0'>
<input type='hidden' name='SelectTag' value=1>
```

config內照著填就是了

mac和Linux用戶自行把webdriver改成其他瀏覽器

## 4. Note

2024/09/12:

看了一下原始碼跟測試，驗證碼發給後端verify_captcha.php檢查，再return 1或0回來給前端

所以直接request.post帳號密碼給https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/login.php就可以登入了

自從有驗證碼到現在才發現，老方法還可以用，哈哈啦我是傻逼小丑

2024/09/17:

無聊弄了個go版本的，不去解驗證碼

2024/09/18:

不小心把帳密push上來了，重開一個呵呵
有空再來弄goroutines 順便把設定區域移到yaml或json

2024/10/09:
如果改成必須單一入口登入可以參考[這篇](https://github.com/chimingwang69/ccuSSO_keep_login)
