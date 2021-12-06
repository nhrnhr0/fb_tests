
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import re
import time
import secrets
MAX_RETRY = 4
def scroll_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
def extract_group_info(driver, group_id, retry=0):
    url = f'https://www.facebook.com/groups/{group_id}/members'
    driver.implicitly_wait(10)
    driver.get(url)
    driver.implicitly_wait(10)
    # find href="/groups/212206742159042/members/"
    try:
        members_counter_link = driver.find_element(By.XPATH, "//a[@href='/groups/212206742159042/members/']")
        print(members_counter_link.text)
    except:
        if retry < MAX_RETRY:
            extract_group_info(driver=driver, group_id=group_id, retry=retry+1)
    
    scroll_bottom(driver)
    user_links = set()
    i = 0
    last_all_links = []
    while True:
        # href="/groups/212206742159042/user/100004484409164/"
        start = time.time()
        all_links = driver.find_elements(By.TAG_NAME,'a')
        # remove the last_all_links from all_links
        # facebook token
        # 
        all_links = [link for link in all_links if link not in last_all_links]
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
        scroll_bottom(driver)
        # sleep for 1 second
        time.sleep(1)
        scroll_bottom(driver)
        # sleep for 2 second
        time.sleep(2)
        scroll_bottom(driver)
        # sleep for 3 second
        time.sleep(3)
        end = time.time()
        print(end-start)
    pass
def main():
    # start chromium browser on link https://www.facebook.com/groups/212206742159042/members
    options =  webdriver.ChromeOptions()
    options.add_argument('--disable-notifications')

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.facebook.com/")
    driver.implicitly_wait(10)
    login(driver, secrets.USERNAME, secrets.PASSWORD)
    
    url = '212206742159042'
    data = extract_group_info(driver, url)
    
    driver.close()
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