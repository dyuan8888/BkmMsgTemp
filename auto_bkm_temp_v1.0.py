# -*- coding: utf-8 -*-
"""
Developed on Jan 3, 2020
@author: DanielYuan
@Email: danielyuan@amecnsh.com
"""

import requests, lxml, os, json
from lxml import etree
from docxtpl import DocxTemplate, RichText
from multiprocessing import Pool
from auto_login import *
from progressbar import *
import time


with open('approvers_list.json') as fb:
    approvers_list = json.load(fb)


def get_bkm_detail_urls(page_text):
    ''' Analyze the bkm in-process page source and get the bkm detail urls''' 
    tree = etree.HTML(page_text)
    # select bkms based on "BKM Board [pending]"
    bkm_nums = tree.xpath("//div[@id='todolist']/table//td[contains(text(),'BKM Board [Pending]')]/preceding-sibling::td[4]/text()")  
    bkm_nums.sort(key=lambda x:(len(x),x))  # sort the list by length and then value
    print(bkm_nums)
    detail_urls = []
    for bkm_num in bkm_nums:
        detail_url = 'http://bkm.amecnsh.com/bkm/index.php/index/admin_viewbkmwithmeeting/bkm_no/' + bkm_num + '.html'
        detail_urls.append(detail_url)
        
    return detail_urls

    
def get_bkm_details(bkm_detail_page_text):
    '''Analyze the bkm detail page data'''
    tree = etree.HTML(bkm_detail_page_text)
    bkm_no = tree.xpath('//h3/text()')[0]    
    bkm_title = tree.xpath('//div[6]/div[2]//tr[1]/td[2]/text()')[0]    
    author = tree.xpath('//h5/text()')[0].split(':')[1].strip()    
    li_list = tree.xpath('//div[@id="bkm_comments_table03"]/table/tbody/tr[4]/td[2]/ul/li')
    approvers = [li.xpath('./span/text()') for li in li_list[:-2]]
    create_date = tree.xpath('//h5/span/text()')[0]    
    bkm_pdf_link = tree.xpath('//div[@id="view_bkm"]//a/@href')[0] 
    appr_list = []     
    for approver in approvers:         
        if approver[0].split('(')[0] in ['Jeremy Chang','Songliu Xu','Rich Chen']:
            appr_dept = approvers_list["apprv_bkup_dict"][approver[-1].strip(';')]
        else:
            appr_dept = approvers_list["appr_dict"][approver[0].split('(')[0]]
        # appr_depts.append(appr_dept)

        appr_list.append({'appr':approver[0].split('(')[0] + ', ' + approver[1].strip(';'), 'appr_dept': appr_dept})
    appr_list.extend(approvers_list["region_appr_lists"])
    
    return bkm_no, bkm_title, author, appr_list, create_date, bkm_pdf_link


def make_doc_file(bkm_info_list):
    '''Gegernate a BKM meeting invitation message'''
    tpl = DocxTemplate('meeting_invitation_message_template.docx')        
    result = []   
    for bkm_info in bkm_info_list:
        dic = {}               
        dic['bkm_nums'] = bkm_info.get()[0]
        bkm_pdf_link = bkm_info.get()[5]
        rt = RichText()
        rt.add(bkm_info.get()[1], url_id=tpl.build_url_id(bkm_pdf_link), color='blue', underline=True)
        dic['bkm_titles'] = rt
        dic['authors'] = bkm_info.get()[2]
        dic['apprs'] = bkm_info.get()[3]            
        dic['create_dates'] = bkm_info.get()[4]      

        result.append(dic)
    print('成功获取BKM数据, 正在将数据写入模板......')
    context = {'bkm': result}
    
    tpl.render(context)
    tpl.save('meeting_invitation_message.docx')


def get_detail_page(ses, detail_url):
    ''' Get the bkm detail pages'''

    return visit_webpage(ses,detail_url)
      

def main():
        
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0', 
    }

    with open('account.json') as fb:
        account = json.load(fb)
    username= account['user']
    password= account['pwd'] 
    login_url = 'http://bkm.amecnsh.com/bkm/index.php/login/login.html'
    bkm_url = 'http://bkm.amecnsh.com/bkm/index.php/index/inprocess.html'  
    print('开始登录BKM Management System...')
    
    browser = login(login_url, username, password)  
    cookies = get_cookie(browser)  # get cookies
    ses = update_session(cookies)   # update the session
    page_text = visit_webpage(ses, bkm_url) # get the page source
        

    print('正在获取如下BKM数据, 请稍候......')
    detail_urls = get_bkm_detail_urls(page_text) # get the urls for bkm detail pages
    # Create a progressbar
    widgets = ['获取BKM页面进度: ', Percentage(), ' ', Bar('■')]
    pbar = ProgressBar(widgets=widgets).start()
    pool = Pool(4) # Create a process pool
    bkm_detail_page_texts = []
    for i in range(len(detail_urls)): 
        bkm_detail_page_text = pool.apply_async(get_detail_page, (ses,detail_urls[i]))
        bkm_detail_page_texts.append(bkm_detail_page_text)
        time.sleep(0.5)
        pbar.update(i*10)
    pool.close()
    pool.join() 
    pbar.finish()

    widgets = ['获取BKM数据进度: ', Percentage(), ' ', Bar('■')]
    pbar = ProgressBar(widgets=widgets).start()
    pool = Pool(4)
    bkm_info_list = []
    for i in range(len(bkm_detail_page_texts)):        
        bkm_info = pool.apply_async(get_bkm_details, (bkm_detail_page_texts[i].get(),))
        bkm_info_list.append(bkm_info)
        time.sleep(0.2)
        pbar.update(i*10)
    pool.close()
    pool.join()
    pbar.finish()  

    make_doc_file(bkm_info_list) # write the data into the template
    print('BKM数据已成功写入模板, 您可以在Word中直接发送邮件或复制到邮件中发送!!!')


if __name__ == '__main__':
    main()
    





