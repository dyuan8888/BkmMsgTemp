from selenium import webdriver
import requests
import os
import json


with open('account.json') as fb:
    account = json.load(fb)
url="http://bkm.amecnsh.com/bkm/index.php/login/login.html"
bkm_url = 'http://bkm.amecnsh.com/bkm/index.php/index/inprocess.html'
data = {'username':account['user'], 'password':account['pwd']}


def auto_login():
    '''Use selenium to log in to the system and keep the session for other web page visit'''  
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless') 
    options.add_argument('--disable-gpu')
    browser = webdriver.Firefox(options=options)
    browser.get(url)
    browser.find_element_by_name('username').send_keys(username)
    browser.find_element_by_name('password').send_keys(password)
    browser.find_element_by_class_name('but_ie').click()
    return browser


def get_cookie(browser):
    '''get cookies from the browser'''
    cookies = browser.get_cookies()
    # print(cookies)
    browser.close()
    return cookies


def update_session(ses,cookies):
    '''update the session with new cookies'''
    c = requests.cookies.RequestsCookieJar() 
    for item in cookies:
        c.set(item["name"],item["value"])
    ses.cookies.update(c)
    return ses


def visit_webpage(ses, url):
    '''visit any webpages with session alive'''
    return ses.get(url=url).text
    

def save_cookies(cookies):
    with open('cookies.json', 'w') as fb:
        json.dump(cookies, fb)


def load_cookies():
    with open('cookies.json') as fb:
        return json.load(fb)
    

def get_page_text():    
    ses = requests.session()
    ses.post(url=url, data=data)  # log in    
    cookies = load_cookies()  # load the pre-saved cookies
    ses = update_session(ses,cookies)   # update the session
    page_text = visit_webpage(ses, bkm_url) # continue to visit other webpages with this session
    if username not in page_text:
        browser = auto_login()  # login
        cookies = get_cookie(browser)  # get cookies
        save_cookies(cookies)
        ses = update_session(ses,cookies)   # update the session
        page_text = visit_webpage(ses, bkm_url)

    return page_text


if __name__ == '__main__':
    get_page_text()