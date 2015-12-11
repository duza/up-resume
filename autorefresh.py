#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyvirtualdisplay import Display
from selenium import webdriver
from datetime import datetime, timedelta
from random import randint
from selenium.common.exceptions import ElementNotVisibleException
import time
import pickle
import os
import pynotify


def givelogin():
    ''' This function return a dictionary 'table' that have
    email and pass from file 't389.c3m' which store in
    /think directory.
       table['email'] -> email
       table['pass'] -> password
    '''
    with open(path_to_file()+'/../think/t389.c3m','rb') as file:
        table = pickle.load(file)
    return table

def note_desktop(s):
    pynotify.init("Resume")
    n = pynotify.Notification('Resume on tut.by',s)
    n.show()

def path_to_file():
    return os.path.abspath(os.path.dirname(__file__))

def reclog(info):
    with open(path_to_file()+'/logfile','ab') as logfile:
        logfile.write(info)

def updateresume():
    try:
        # start virtual display
        display = Display(visible=0, size=(640, 480))
        display.start()
        reclog('Display started. PID ={}\r\n'.format(display.pid))
        # select settings
        browser = webdriver.Firefox()
        browser.maximize_window()
        browser.implicitly_wait(9)
        # get a site
        browser.get(u'http://jobs.tut.by/login')
        # enter your email
        email = browser.find_element_by_name(u'username')
        table = givelogin()
        email.send_keys(table['email'])
        # enter your password
        password = browser.find_element_by_name(u'password')
        password.send_keys(table['pass'])
        # sign in your account
        signin = browser.find_element_by_xpath(u"//input[@type='submit' and @value='Войти в личный кабинет']")
        signin.click()
        # enter in your resumes
        browser.get(u'http://jobs.tut.by/applicant/resumes')
        # select resume
        junior = browser.find_element_by_partial_link_text(u'junior')
        junior.click()
        # update it
        refreshjun = browser.find_element_by_class_name(u'HH-Resume-Touch-Button')
        refreshjun.click()
        # exit from session
        logout = browser.get(u'http://jobs.tut.by/account/logout')
        # from browser
        browser.quit()
        display.stop()
        now = datetime.now()
        reclog('Resume updated {}.\r\n'.format(now))
        return now

    except ElementNotVisibleException as NOTelement:
        reclog("Sorry, but element is not visible on page\r\n"+str(NOTelement))
        now = datetime.now()
        reclog('\r\nResume was not update {}.\r\n'.format(now))
        return None

def main():
    while True:
        try:
            with open(path_to_file()+'/temp', 'r+b') as file:
                previoustime = pickle.load(file)
                now = datetime.now()
                diff = now - previoustime
                if diff > timedelta(minutes=720):
                    reclog("Already passed 12 hours. Update announcment.\r\n")
                    now = updateresume() or previoustime
                    file.seek(0)
                    pickle.dump(now, file)
                    return "PLZ, UPDATE ANN!"
                else:
                    reclog('Little time has passed. Please wait...\r\n')
#                    time.sleep((timedelta(minutes=240)-diff).total_seconds())
#                    now = updateresume() or previoustime
#                    file.seek(0)
#                    pickle.dump(now, file)
                    return "Try UPD ANN later."
        except Exception as error:
            reclog(str(error)+'\r\n')
            raise

if __name__ == "__main__":
    note_desktop(main())
