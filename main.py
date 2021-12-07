
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import re
import time
import secrets
from facebook_scraper import get_profile
import requests
MAX_RETRY = 4

def scroll_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    return driver.execute_script("return window.pageYOffset;")

def get_username_from_fb_id(fb_id):
    response = requests.get(f"https://m.facebook.com/{fb_id}")
    m = re.search('<link rel="canonical" href="(.*?)"', response.text)
    if m and len(m.groups()) > 0:
        return m.groups()[0]
    else:
        return None
    #print(response.text)

def mySleep(t):
    print('sleeping: ', t)
    time.sleep(t)
def extract_group_info(driver, group_id, retry=0):
    url = f'https://www.facebook.com/groups/{group_id}/members'
    driver.implicitly_wait(10)
    driver.get(url)
    driver.get(url)
    driver.implicitly_wait(10)
    # find href="/groups/212206742159042/members/"
    '''
    try:
        members_counter_link = driver.find_element(By.XPATH, f"//a[@href='/groups/{group_id}/members/']")
        print(members_counter_link.text)
    except:
        if retry < MAX_RETRY:
            extract_group_info(driver=driver, group_id=group_id, retry=retry+1)
    '''
    user_links = set()
    i = 0
    last_all_links = []
    stop_loop_counter = False
    STOP_LOOP_COUNTER_LIMIT = 10
    last_scroll_position = 0
    while stop_loop_counter < STOP_LOOP_COUNTER_LIMIT:
        save_group_info(user_links, group_id + '.csv')
        for m in range(0, 20):
            scroll_bottom(driver)
            # sleep for 1 secound and the last_scroll_position / 1000
            mySleep(1 + last_scroll_position / 100000)
        mySleep(5)
        current_scroll = scroll_bottom(driver)
        if current_scroll == last_scroll_position:
            stop_loop_counter += 1
        else:
            stop_loop_counter = 0
            last_scroll_position = current_scroll
            
        print('start working...')
        driver.implicitly_wait(4)
        # href="/groups/212206742159042/user/100004484409164/"
        start = time.time()
        all_links = driver.find_elements(By.TAG_NAME,'a')
        
        # remove the last_all_links from all_links
        # facebook token
        # 
        all_links = all_links[len(last_all_links):]#[link for link in all_links if link not in last_all_links]
        last_all_links += all_links
        print('scanning: ' ,len(all_links), '/', len(last_all_links), ' found: ', len(user_links))
        for link in all_links:
            if link.get_attribute('href') is not None:
                if link.get_attribute('href').startswith(f'https://www.facebook.com/groups/{group_id}/user/'):
                    if link.get_attribute('href') not in user_links:
                        html = link.get_attribute('innerHTML')
                        m = re.search('aria-label="(.+?)"', html)
                        if m and len(m.groups()) > 0:
                            name = m.groups()[0]
                            #print(name)
                        else:
                            m = re.search('<', html)
                            if not m:
                                name = link.get_attribute('innerHTML')
                            else:
                                continue
                        link_str = link.get_attribute('href')
                        data = link_str + '||' + str(name)
                        user_links.add(data)
        print('done: ', time.time() - start, ' sleeping for 3 secs')
        time.sleep(3)
        #print(end-start)
    return user_links
    pass
import random

def main():
    # https://facebook.com/100000346982800
    #ret = get_profile("100000346982800") # Or get_profile("zuck", cookies="cookies.txt")
    #get_username_from_fb_id("100000346982800")
    
    #print(ret)
    #return
    # start chromium browser on link https://www.facebook.com/groups/212206742159042/members
    options =  webdriver.ChromeOptions()
    options.add_argument('--disable-notifications')

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.facebook.com/")
    driver.implicitly_wait(10)
    login(driver, secrets.USERNAME, secrets.PASSWORD)
    
    group_id = '198255094715278'
    data = extract_group_info(driver, group_id)
    print(f'done extracting group info {group_id}: {len(data)}')
    
    save_group_info(data, group_id + '.csv')
    driver.close()
    pass

import csv
def save_group_info(data, filename='group_info.csv'):
    with open(filename, 'w', newline='', encoding="UTF-16") as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for item in data:
            writer.writerow(item.split('||'))
    pass

def login(driver, username, password):
    driver.find_element(By.ID, "email").send_keys(username)
    #driver.find_element(By.ID, "email").send_keys(Keys.RETURN)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.ID, "pass").send_keys(Keys.RETURN)
    driver.implicitly_wait(10)
    pass


if __name__ == '__main__':
    main()