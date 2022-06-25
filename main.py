#!/usr/bin/python3
# coding=utf-8
from webbrowser import get
import requests
import time
import json
import sys
from urllib import parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import ocr_captcha
from selenium.webdriver.chrome.options import Options


from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')
# 填写webdriver的保存目录
driver = webdriver.Chrome(chrome_options=chrome_options,executable_path='/root/reportHealth/chromedriver')

# 填写学号和密码
username = "**********"
password = "**********"

# 记得写完整的url 包括http和https
login_url = "http://ehall.wtu.edu.cn/qljfwapp/sys/lwWtuPassCodeSchool/*default/index.do?null#/studentDetail"
studentName = ""

def login():
    driver.get(login_url)

    input_username = driver.find_element_by_id('username')
    input_password = driver.find_element_by_id('password')
    input_captch = driver.find_element_by_id('captchaResponse')

    input_username.send_keys(username)
    input_password.send_keys(password)
    # 先截图验证码图片 ，再调用ocr_capthcha.py 将验证码识别结果存入'captcha.txt'文件中
    # 目前 chrome 直接用screenshot 有bug ,firefox 没有
    driver.maximize_window()
    
    driver.save_screenshot('capture.png')    #全屏截图
    
    ele = driver.find_element_by_id('captchaImg')
    ele.screenshot('ele.png')    #元素截图

    input_captch.send_keys(ocr_captcha.ocr())

    # 调用load_ocr函数读取'captcha.txt'文件 ，再将captcha_key输入
    # 再点击登录

    time.sleep(5)
    input_captch.send_keys(Keys.ENTER)
    # login_button = driver.find_element_by_class_name('auth_login_btn primary full_width')
    
    # login_button.click()

    time.sleep(10)
    
    try:    
        studentId = driver.find_elements_by_xpath('/html/body/div[1]/div/div[1]/div[2]/div[4]')[0].text
    except IndexError as E:
        print("登录失败")
        driver.close
        return False
    else:
        if(studentId == username):
            global studentName
            studentName = driver.find_elements_by_xpath('/html/body/div[1]/div/div[1]/div[2]/div[1]')[0].text
            print("登录成功")
            return True

def get_Cookie():
    driver.get(login_url)

    time.sleep(5)

    report_url = "http://ehall.wtu.edu.cn/qljfwapp/sys/lwWtuPassCodeSchool/*default/index.do?null#/report"
    driver.get(report_url)
    with open('cookies.txt','w') as f:
        # 将cookies保存为json格式
        f.write(json.dumps(driver.get_cookies()))

    driver.close()

def join_Cookie():
    with open('cookies.txt') as f:
    # 将cookies保存为json格式
        cookies = json.load(f)

    route=""
    _WEU=""
    iPlanetDirectoryPro=""
    JSESSIONID=""
    MOD_AUTH_CAS=""

    for cookie in cookies:
            if (cookie['name'] == 'route'):
                route = cookie['value']
                continue
            if (cookie['name'] == '_WEU'):
                _WEU = cookie['value']
                continue
            if (cookie['name'] == 'iPlanetDirectoryPro'):
                iPlanetDirectoryPro = cookie['value']
                continue
            if (cookie['name'] == 'JSESSIONID'):
                JSESSIONID = cookie['value']
                continue
            if (cookie['name'] == 'MOD_AUTH_CAS'):
                MOD_AUTH_CAS = cookie['value']
                continue
        
    cookieStudent = "route=" + route + "; "
    cookieStudent += "_WEU=" + _WEU + "; "
    cookieStudent += "iPlanetDirectoryPro=" + iPlanetDirectoryPro + "; "
    cookieStudent += "JSESSIONID=" + JSESSIONID + "; "
    cookieStudent += "MOD_AUTH_CAS=" + MOD_AUTH_CAS

    return cookieStudent

def reportRequests(Cookie):
    timeNow = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    
    cookieStudent = Cookie

    head={
    'Connection': 'keep-alive',
    'Content-Length': '522',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Redmi K20 Pro Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/98.0.4758.101 Mobile Safari/537.36 wxwork/4.0.0 ColorScheme/Light MicroMessenger/7.0.1 NetType/WIFI Language/zh Lang/zh',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin':'http://ehall.wtu.edu.cn',
    'Referer':'http://ehall.wtu.edu.cn/qljfwapp/sys/lwWtuPassCodeSchool/*default/index.do?null',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cookie': cookieStudent,
    }
    Url = 'http://ehall.wtu.edu.cn/qljfwapp/sys/lwWtuPassCodeSchool/api/reportHealth.do'
    datas = {
        'USER_ID':username,
        'USER_NAME':studentName,
        'DEPT_NAME':'',
        'HEALTH_CODE':'绿色',
        'HEALTH_STATE':'健康',
        'CURRENT_TEMP':'36.5',
        'IS_SELF_FEVER':'否',
        'IS_SELF_COUGH':'否',
        'IS_FAMILY_FEVER':'否',
        'IS_FAMILY_COUGH':'否',
        'DETAIL_CONDITION':'',
        'REPORT_TIME':timeNow,
        'CURRENT_LOCATION':'湖北省武汉市江夏区阳光大道1号',
        'LONGITUDE':'114.34446469479609',
        'LATITUDE':'30.381956623916015',
        'CAN_REPORT':'YES',
    }
    datatext = parse.urlencode(datas)
    endResponse = requests.post(Url,data=datatext,headers=head)
    endJson = json.loads(endResponse.content.decode('utf-8', 'ignore'))
    if(endJson['data']['success']):
        print(timeNow + "打卡成功")
        return True

if __name__ == '__main__':
    while(True):
        if (login()):
            get_Cookie()
            Cookie = join_Cookie()
            if(reportRequests(Cookie)):
                sys.exit()
            else:
                continue
        else:
            continue
