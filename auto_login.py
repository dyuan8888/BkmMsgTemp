from selenium import webdriver
import requests
import os

'''Use selenium to log in to the system and keep the session for other web page visit'''


url="http://bkm.amecnsh.com/bkm/index.php/login/login.html"
bkm_url = 'http://bkm.amecnsh.com/bkm/index.php/index/inprocess.html'

def login(url, username, password):
    '''Log in to the system
    url: web url
    username:
    password:
    return: browser
    '''  
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

def update_session(cookies):
    '''update the session with new cookies'''
    c = requests.cookies.RequestsCookieJar() 
    for item in cookies:
        c.set(item["name"],item["value"])
    ses = requests.Session()
    ses.cookies.update(c)
    return ses

def visit_webpage(ses, url):
    '''visit any webpages with session alive'''
    page_text = ses.get(url=url).text
    return page_text



def main():
    username= os.getenv('username')
    password= os.getenv('password')
    browser = login(url, username, password)  # login
    cookies = get_cookie(browser)  # get cookies
    ses = update_session(cookies)   # update the session
    page_text = visit_webpage(ses, bkm_url) # continue to visit other webpages with this session
    print(page_text)

if __name__ == '__main__':
    main()