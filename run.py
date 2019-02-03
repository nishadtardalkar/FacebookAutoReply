from manage import begin
import webbrowser
from threading import Thread
from urllib import request
from fbreply.Webdriver import webdriver
from fbreply.CustomDjango import basehttp
from selenium.common.exceptions import NoSuchElementException
from fbreply import monitor_and_reply

def post_start():
    waiting = True
    while waiting:
        try:
            request.urlopen("http://127.0.0.1:8000")
            waiting = False
        except:
            None

    main_ui = webdriver.WebDriver()
    main_ui.get("http://127.0.0.1:8000")

    while True:
        try:
            main_ui.find_element_by_tag_name("abcd")
        except NoSuchElementException as e:
            None
        except Exception as e:
            break
    basehttp.stop()
    monitor_and_reply.stop_monitor()

Thread(target=post_start).start()
begin(["manage.py", "runserver", "--noreload"])
