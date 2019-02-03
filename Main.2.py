from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import datetime

month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def MonthToInt(x):
    try:
        return month_list.index(x)
    except:
        return -1

def CompareDate(x, y):    
    if x[2] > y[2]:
        return True
    elif x[2] == y[2]:
        if x[1] > y[1]:
            return True
        elif x[1] == y[1]:
            if x[0] >= y[0]:
                return True
    return False

def StringToDate(x):
    x = x.split("at")
    if len(x) == 1:
        return [c_day, c_month, c_year]
    if x[0] == "Yesterday":
        if c_day == 1:
            if c_month == 0:
                return [31, 11, c_year-1]
            return [31, c_month-1, c_year]        
        return [c_day-1, c_month, c_year]
    x = x[0]
    x = x.split()
    x[0] = int(x[0])
    x[1] = MonthToInt(x[1])
    if len(x) == 2:
        x.append(c_year)
    else:
        x[2] = int(x[2])
    return x

def KeywordInComment(x):
    # COMPARE
    return 0

    
c_year = datetime.datetime.now().year
c_day = datetime.datetime.now().day
c_month = datetime.datetime.now().month - 1
keywords_and_replies = [["","Works"]]

browser_options = Options()  
#browser_options.add_argument("--headless")  
driver = webdriver.Firefox(options=browser_options)


driver.get("https://www.amazon.in")
a = driver.find_element_by_id("nav-logo")
a.click()
WebDriverWait(driver, 1000000).until(EC.staleness_of(a))
print("OK")
exit(0)

# BEGIN LOGIN
driver.get("http://m.facebook.com")
elem = driver.find_element_by_name("email")
elem.clear()
elem.send_keys("fashark@linuxmail.org")
elem = driver.find_element_by_name("pass")
elem.clear()
elem.send_keys("chelseachamp")
#elem.send_keys("12")
elem = driver.find_element_by_name("login")
elem.click()  

page = input("Page : ")
driver.get(page)
driver.execute_script("document.getElementById('m-timeline-cover-section').remove()")
till_date = input("Date (D Month YYYY) : ")
till_date = StringToDate(till_date)

# GET POSTS FROM PAGE
posts = []
find_more = True
load_more = 1
while find_more and load_more:
    load_more = None
    a_tags = driver.find_elements_by_tag_name("a")
    for i in a_tags:
        innertext = i.get_attribute("innerText")
        if "Comment" in innertext:
            dated = i.find_element_by_xpath("..").find_element_by_xpath("..").find_element_by_tag_name("abbr").get_attribute("innerText")
            dated = StringToDate(dated)
            if CompareDate(dated, till_date):
                posts.append(i.get_attribute("href"))
            else:
                find_more = False
                break
        elif "Show more" in innertext or "See more stories" in innertext:
            #break
            load_more = i.get_attribute("href")
    if find_more and load_more:
        driver.get(load_more)
        driver.execute_script("document.getElementById('m-timeline-cover-section').remove()")

print(posts[0])
print(len(posts))
#exit(0)

# GET RELATIVE COMMENTS FROM POSTS
comments = []
for post in posts:
    driver.get(post)
    load_more = 1
    while load_more:
        load_more = None
        a_tags = driver.find_elements_by_tag_name("a")
        for i in a_tags:
            innertext = i.get_attribute("innerText")
            if "Reply" in innertext:
                p = i.find_element_by_xpath("..").find_element_by_xpath("..")
                comment_elements = p.find_elements_by_xpath("*")
                if len(comment_elements) > 4:
                    if "You" in comment_elements[4].find_element_by_tag_name("a").get_attribute("innerText"):
                        load_more = None
                        break
                comment_text = comment_elements[1].get_attribute("innerText")
                reply = KeywordInComment(comment_text)
                if reply >= 0:
                    comments.append([i.get_attribute("href"), keywords_and_replies[reply]])
            if "View more comments" in innertext:
                load_more = i.get_attribute("href")
        if load_more:
            driver.get(load_more)

print(len(comments))

# REPLY TO COMMENTS
for comment in comments:
    driver.get(comment[0])
    reply_box = driver.find_element_by_id("composerInput")
    reply_box.send_keys(comment[1])
    form = driver.find_element_by_tag_name("form")
    form.submit()

