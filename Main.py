from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains


chrome_options = Options()  
#chrome_options.add_argument("--headless")  
#driver = webdriver.Edge(options=chrome_options)
driver = webdriver.Firefox()
driver.get("http://m.facebook.com")
actions = ActionChains(driver)

elem = driver.find_element_by_name("email")
elem.clear()
elem.send_keys("fashark@linuxmail.org")
elem = driver.find_element_by_name("pass")
elem.clear()
elem.send_keys("chelseachamp")
elem = driver.find_element_by_name("login")
elem.click()

post_feed = WebDriverWait(driver, 500000000).until(EC.presence_of_element_located((By.ID, 'm_newsfeed_stream'))).find_elements_by_tag_name("div")[2]
posts = post_feed.find_elements_by_xpath("*")
for i in posts:
    x = i.find_elements_by_xpath("*")
    for j in x:
        if j.get_attribute("data-ft") != None:
            x = j            
            break
    x = x.find_elements_by_xpath("*")[1]
    x = x.find_elements_by_tag_name("a")
    for j in x:
        if "Comment" in j.get_attribute("innerText"):
            x = j
            break
    prev_count = len(driver.window_handles)
    x.send_keys(Keys.CONTROL + Keys.RETURN)
    while prev_count == len(driver.window_handles):
        continue
    driver.switch_to.window(driver.window_handles[-1])
    comments = WebDriverWait(driver, 500000000).until(EC.presence_of_element_located((By.ID, 'm_story_permalink_view'))).find_elements_by_xpath("*")[1].find_elements_by_xpath("*")[0].find_elements_by_xpath("*")[3].find_elements_by_xpath("*")
    for j in comments:
        p = j.find_elements_by_xpath("*")[0]
        text = p.find_elements_by_xpath("*")[1]
        z = p.find_elements_by_xpath("*")[3].find_elements_by_tag_name("a")
        for k in z:
            if k.get_attribute("innerText") == "Reply":
                z = k
                break
        prev_count = len(driver.window_handles)
        z.send_keys(Keys.CONTROL + Keys.RETURN)
        while prev_count == len(driver.window_handles):
            continue
        driver.switch_to.window(driver.window_handles[-1])

        comment = WebDriverWait(driver, 500000000).until(EC.presence_of_element_located((By.ID, 'root'))).find_elements_by_xpath("*")[0].find_elements_by_xpath("*")[1].find_elements_by_xpath("*")[0].find_elements_by_xpath("*")[1].get_attribute("innerText")

        # MAKE A CHECK FOR KEYWORDS IN COMMENT****
        keyword_found = True

        if keyword_found:
            reply = driver.find_element_by_id("composerInput")
            reply.send_keys("Gaben is watching...")
            submit = driver.find_elements_by_tag_name("input")
            for k in submit:
                if k.get_attribute("value") == "Reply":
                    k.click()
                    break

        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
            
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])

