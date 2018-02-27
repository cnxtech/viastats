#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 

import os
import time
import sys
import json

URL = 'https://account.viasat.com'
USERNAME = os.environ['VIASTATS_USERNAME']
PASSWORD = os.environ['VIASTATS_PASSWORD']
TIMEOUT = 300

def handler(event, context):

    url = event.get('url') or URL

    try:
        os.mkdir('/tmp/data-path')
    except FileExistsError:
        pass

    try:
        os.mkdir('/tmp/cache-dir')
    except FileExistsError:
        pass

    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')

    chrome_options.binary_location = 'headless-chrome/headless_shell'

    driver = webdriver.Chrome(
        executable_path='headless-chrome/chromedriver',
        chrome_options = chrome_options
    )

    vurl = 'usage'
    #vurl = 'federation/SSORedirect/metaAlias/idp'
    ret = driver.get('%s/%s' % (url, vurl))
    driver.save_screenshot('prelogin.png')

    try:
        e = WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("IDToken1"))
        e.clear()
        print('sending username')
        e.send_keys(event.get('username'))

        e = WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("IDToken2"))
        e.clear()
        print('sending password')
        e.send_keys(event.get('password'))

        e = WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("Login.Submit"))
        print('clicking login')
        webdriver.ActionChains(driver).move_to_element(e).click(e).perform()

        driver.save_screenshot('postlogin.png')
        #ret = driver.get('%s/%s' % (url, vurl))

        print('waiting for current data usage...')
        e = WebDriverWait(driver, 30).until(lambda x: x.find_elements_by_xpath("//*[contains(text(), 'Current data usage')]"))
        print('found')
        driver.save_screenshot('current-data-usage.png')

        #print('waiting for usage-data...')
        #e = WebDriverWait(driver, 30).until(lambda x: x.find_element_by_id("usage-data"))
        #print('found: %s' %  e.text)
        #driver.save_screenshot('usage-data.png')

        print('waiting for flat-usage...')
        e = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((By.ID, "flat-usage")))
        print('found!')
        driver.save_screenshot('usage.png')

    except TimeoutException as ex:
        print('Timeout: %s' % repr(ex))
        driver.save_screenshot('timeout.png')

    driver.close()
    return ret

if __name__ == '__main__':
    event = {}
    event['url'] = URL
    event['username'] = USERNAME
    event['password'] = PASSWORD
    event['timeout'] = TIMEOUT 
    ret = handler(event, None)
    print('%s' % json.dumps(ret, sort_keys=True))
