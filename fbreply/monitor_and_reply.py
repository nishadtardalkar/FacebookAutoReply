from fbreply.Webdriver import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import datetime
import json
from threading import Thread
import random
import os

month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def MonthToInt(x):
    global month_list
    try:
        return month_list.index(x) + 1
    except:
        return -1

def CompareDate(x, y):
    if x[2] > int(y[2]):
        return True
    elif x[2] == int(y[2]):
        if x[1] > int(y[1]):
            return True
        elif x[1] == int(y[1]):
            if x[0] >= int(y[0]):
                return True
    return False

c_year = datetime.datetime.now().year
c_day = datetime.datetime.now().day
c_month = datetime.datetime.now().month - 1
def StringToDate(x):
    global c_year
    x = x.split()
    x[0] = int(x[0])
    x[1] = MonthToInt(x[1])
    if len(x) == 2:
        x.append(c_year)
    else:
        x[2] = int(x[2])
    return x

kr_list = []
def KeywordInComment(x):
    global kr_list
    x = x.encode('unicode-escape').decode('utf-8')
    x = x.lower()
    for i in range(len(kr_list)):
        for j in kr_list[i][0]:
            if j in x:
                r = random.randint(0, len(kr_list[i][1])-1)                
                return kr_list[i][1][r]
    return -1

def login(email, password, driver):
    driver.get("https://m.facebook.com/")
    e = driver.find_element_by_name("email")
    p = driver.find_element_by_name("pass")
    l = driver.find_element_by_name("login")
    driver.execute_script("arguments[0].value = arguments[1];", e, email)
    driver.execute_script("arguments[0].value = arguments[1];", p, password)
    l.click()
    WebDriverWait(driver, 500000000).until(EC.staleness_of(l))
    if driver.find_element_by_tag_name("h3").get_attribute("innerText") == "Log in with one tap":
        name = driver.find_elements_by_tag_name("tbody")[1].find_elements_by_xpath("*")[0].find_elements_by_xpath("*")[1].get_attribute("innerText")
    else:
        name = driver.find_element_by_id("mbasic_logout_button").get_attribute("innerText")[9:-1]
    #driver.get("https://m.facebook.com/profile/questions/view/")
    #actor_id = driver.find_element_by_name("question").get_attribute("value")[:-2]
    #return [name, actor_id]
    return [name]

def get_comment_pages(driver, page, till_date):
    global active
    driver.get(page)
    driver.execute_script("document.getElementById('m-timeline-cover-section').remove()")
    posts = []
    try:
        find_more = True
        load_more = 1
        while find_more and load_more and active:
            load_more = None
            a_tags = driver.find_elements_by_tag_name("a")
            for i in a_tags:
                innertext = i.get_attribute("innerText")
                if "Comment" in innertext:
                    try:
                        dated = i.find_element_by_xpath("..").find_element_by_xpath("..").find_element_by_tag_name("abbr").get_attribute("innerText")
                        if "at" in dated:
                            dated = StringToDate(dated.split(" at")[0])                 
                            if CompareDate(dated, till_date):
                                posts.append(i.get_attribute("href"))
                            else:
                                find_more = False
                                break
                        else:
                            posts.append(i.get_attribute("href"))           
                    except Exception as e:
                        print("1 : " + str(e))
                        None
                elif "Show more" in innertext or "See more stories" in innertext:
                    load_more = i.get_attribute("href")
            if find_more and load_more and active:
                driver.get(load_more)
                driver.execute_script("document.getElementById('m-timeline-cover-section').remove()")
    except Exception as e:
        print("2 : " + str(e))
        None
    return posts

replied_comments = set()
def get_reply_pages(driver, page, max_comment_pages):
    global replied_comments
    global active
    comments = []
    try:
        driver.get(page)
        load_more = 1
        c = 0
        while load_more and (c < max_comment_pages or max_comment_pages == 0) and active:
            load_more = None
            a_tags = driver.find_elements_by_tag_name("a")
            for i in a_tags:
                innertext = i.get_attribute("innerText")
                if "Reply" == innertext:
                    try:
                        href = i.get_attribute("href")
                        cid = href.split("=")[1].split("&")[0]
                        if cid in replied_comments:
                            continue
                        replied_comments.add(cid)
                        p = i.find_element_by_xpath("..").find_element_by_xpath("..")
                        comment_elements = p.find_elements_by_xpath("*")
                        comment_text = comment_elements[1].get_attribute("innerText")
                        reply = KeywordInComment(comment_text)
                        #print(comment_text, reply)
                        if reply != -1:
                            comments.append([page, reply, cid, href])
                    except Exception as e:
                        print("3 : " + str(e))
                        None
                if "View more comments" in innertext and (c < max_comment_pages or max_comment_pages == 0):
                    load_more = i.get_attribute("href")
            if load_more and active:
                c += 1
                driver.get(load_more)
    except Exception as e:
        print("4 : " + str(e))
        None
    return comments

def monitor_thread(driver, pages_dates, max_comment_pages):
    global reply_list
    global active
    reply_list = []
    while active:
        for page in pages_dates:
            comment_pages = get_comment_pages(driver, page[0], page[1])
            if not active:
                break
            for i in comment_pages:
                reply_list.append(get_reply_pages(driver, i, max_comment_pages))
                if not active:
                    break
    print("Closing monitor")
    driver.close()

reply_list = []
account_names = set()
def reply_thread(drivers):
    global log
    global active
    global reply_list
    global comments_replied
    log_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/Logs/"
    log_file = open(log_path + str(len(os.listdir(log_path))) + " " + str(c_day) + "-" + str(c_month) + "-" + str(c_year) + ".txt", "w")
    reply_account = 0
    while active:
        if reply_list:
            comments = reply_list.pop()
            for comment in comments:
                if not active:
                    break
                try:
                    drivers[reply_account].get(comment[0])
                    replied_to_link = ""
                    while True:
                        try:
                            reply_links = drivers[reply_account].find_element_by_id("like_" + comment[2]).find_element_by_xpath("..").find_elements_by_tag_name("a")
                            for possible_link in reply_links:
                                if possible_link.get_attribute("innerText") == "Reply":
                                    replied_to_link = possible_link.get_attribute("href")
                                    drivers[reply_account].get(replied_to_link)
                                    break
                            break
                        except:
                            next_page = drivers[reply_account].find_element_by_id("see_next_" + comment[2].split("_")[0]).find_elements_by_xpath("*")[0]
                            drivers[reply_account].get(next_page.get_attribute("href"))
                    
                    reply = True
                    while True:
                        reply_names = drivers[reply_account].find_elements_by_tag_name("h3")
                        for i in reply_names:
                            if i.get_attribute("innerText") in account_names:
                                reply = False
                                break
                        try:
                            more_replies = drivers[reply_account].find_element_by_id("comment_replies_more_2:" + comment[2])
                            drivers[reply_account].get(more_replies.find_element_by_xpath("*").get_attribute("href"))
                        except:
                            break
                    if reply:
                        reply_box = drivers[reply_account].find_element_by_id("composerInput")
                        #reply_box.send_keys(comment[1])
                        drivers[reply_account].execute_script("arguments[0].innerText = arguments[1];", reply_box, comment[1])
                        form = drivers[reply_account].find_element_by_tag_name("form")
                        form.submit()
                        WebDriverWait(drivers[reply_account], 500000000).until(EC.staleness_of(form))
                        try:
                            if drivers[reply_account].find_element_by_tag_name("h2").get_attribute("innerText") == "Please review your comment":
                                confirm = drivers[reply_account].find_element_by_id("root").find_element_by_tag_name("form").find_elements_by_xpath("*")[2]
                                confirm.click()
                                WebDriverWait(drivers[reply_account], 500000000).until(EC.staleness_of(confirm))
                        except:
                            None                        
                        comments_replied.append(comment[3])
                        log_file.write("Replied to : " + comment[3] + "\n")
                        reply_account += 1
                        if reply_account >= len(drivers):
                            reply_account = 0
                except Exception as e:
                    print("5 : " + str(e))
                    log.append("Reply failed : " + comment[3])
                    log_file.write("Reply failed at : " + comment[3] + "\n")
    print("Closing repliers")
    for i in drivers:
        i.close()
            

def start_monitor(data):
    data = json.loads(data)['data']
    accounts = data[0]
    keywords_replies = data[1]
    pages_dates = data[2]
    max_comment_pages = int(data[3])

    for i in keywords_replies:
        keys = i[0].split(',')
        keys = [key.lower() for key in keys]
        replies = [reply.lower() for reply in i[1]]
        kr_list.append([keys, replies])
    
    browser_options = Options()  
    #browser_options.add_argument("--headless")  
    
    monitor_driver = webdriver.WebDriver(options=browser_options)

    reply_drivers = []
    for i in range(len(accounts)):
        reply_drivers.append(webdriver.WebDriver(options=browser_options))
    
    # Login in monitor driver with 1st account and all accounts on reply drivers
    #acc_info = login(accounts[0][0], accounts[0][1], monitor_driver)
    c = 0
    monitor_login_done = False
    for i in range(len(accounts)):
        try:
            acc_info = login(accounts[i][0], accounts[i][1], reply_drivers[c])
            account_names.add(acc_info[0])          
            c += 1
            if not monitor_login_done:
                login(accounts[i][0], accounts[i][1], monitor_driver)
                monitor_login_done = True
        except:
            reply_drivers[-1].close()
            reply_drivers.pop()
            log.append(accounts[i][0] + " failed to login.")         
    if len(reply_drivers) == 0:
        status = 0
        return 1

    global active
    active = True
    t_monitor = Thread(target=monitor_thread,args=(monitor_driver, pages_dates, max_comment_pages))
    t_reply = Thread(target=reply_thread,args=(reply_drivers,))
    t_monitor.start()
    t_reply.start()
    return 0
    

status = -1
comments_replied = []
log = []
def get_status():
    global log
    global status
    global replied_comments
    global comments_replied
    if status < 0:
        t = log
        log = []
        return {'cm':len(replied_comments), 'cr':len(comments_replied), 'log':t}
    else:
        return {'dead':status}

active = True
def stop_monitor():
    global active
    active = False










        
