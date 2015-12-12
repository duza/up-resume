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
    with open(path_to_file()+'/../../think/t389.c3m','rb') as file:
        table = pickle.load(file)
    return table

def note_desktop(s):
    ''' This function makes possible to notify user when script
    is running. It takes one arg string s and show it on desktop. '''
    pynotify.init("Resume")
    n = pynotify.Notification('Resume on tut.by',s)
    n.show()

def path_to_file():
    return os.path.abspath(os.path.dirname(__file__))

def reclog(info):
    ''' Open logfile an write there information '''
    with open(path_to_file()+'/logfile','ab') as logfile:
        logfile.write(info)

def updateresume():
'''Function try update resume and return time of updating'''
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
        # exit from browser
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
# Open file which store datetime previous updating resume
            with open(path_to_file()+'/temp', 'r+b') as file:
                previoustime = pickle.load(file) #loading prev datetime
                now = datetime.now() # current time
                diff = now - previoustime # how much time has passed
                if diff > timedelta(minutes=300): # if diff > 5 hours
# Then write that Updatin of resume is possible 
                    reclog("Already passed 5 hours. Update announcment.\r\n")
# If function updateresume executed without errors now equal current 
#time - time of updating resume else time remains the same
                    now = updateresume() or previoustime
                    file.seek(0) # turn to top file that store datetime
                    pickle.dump(now, file) # write new datetime in file
                    return "Pls, Update resume!"
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
