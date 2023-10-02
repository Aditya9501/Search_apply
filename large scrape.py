from selenium import webdriver
import pandas as pd
import datetime
import time
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import multiprocessing

naukri = "https://www.naukri.com"
log_in_layer = (By.XPATH,"//a[@id='login_Layer']")
username_details = (By.XPATH,"//input[@placeholder='Enter your active Email ID / Username']")
password_details = (By.XPATH, "//input[@placeholder='Enter your password']")
log_in_click = (By.XPATH,"//button[@type='submit']")

def get_total_urls(user,passcode,jobdesgn,yrsexp):
    driver = webdriver.Chrome()
    driver.get(naukri)
    driver.maximize_window()
    wait = WebDriverWait(driver,10)
    chain = ActionChains(driver)

    # Click on Log-In
    wait.until(EC.element_to_be_clickable(log_in_layer)).click()

    # Input your Detail
    u_d = (By.XPATH,"//input[@placeholder='Enter your active Email ID / Username']")
    wait.until(EC.visibility_of_element_located(u_d)).send_keys(user)
    wait.until(EC.visibility_of_element_located(password_details)).send_keys(passcode)
    wait.until(EC.element_to_be_clickable(log_in_click)).click()
    
    type_job_loc = (By.XPATH,"//span[@class='nI-gNb-sb__placeholder']")
    wait.until(EC.element_to_be_clickable(type_job_loc)).click()

    # Input Designation
    job_type_loc = (By.XPATH, "//input[@placeholder='Enter keyword / designation / companies']")
    wait.until(EC.element_to_be_clickable(job_type_loc)).send_keys(jobdesgn)

    
    # Click on Search
    search_loc =(By.XPATH, "//span[normalize-space()='Search']")
    wait.until(EC.element_to_be_clickable(search_loc)).click()
    
    wait.until(EC.element_to_be_clickable((By.XPATH,"//div[@class='inside']")))
    dragger=driver.find_element(By.XPATH,"//div[@class='inside']")
    chain.move_to_element(dragger).click_and_hold().pause(1).drag_and_drop_by_offset(dragger,(((yrsexp)*7)-210),0).perform()

    wait.until(EC.visibility_of_element_located((By.XPATH, "/html[1]/body[1]/div[1]/div[4]/div[1]/div[1]/section[2]/div[1]/div[1]/span[1]")))
    total_listing = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[4]/div[1]/div[1]/section[2]/div[1]/div[1]/span[1]").text
    pages = float(total_listing.split(" ")[-1])/float(total_listing.split(' ')[2])
    link = driver.current_url
    driver.close()
    
    splitted = link.split('?')
    before = splitted[0]
    after = splitted[1]
    
    total_url = [link]

    for i in range(2,int(pages)+2):
        l = before + f'-{i}?'+after
        total_url.append(l)
    
    return total_url

def get_df(user,passcode,jobdesgn,yrsexp, list_urls):
    driver = webdriver.Chrome()
    driver.get(naukri)
    driver.maximize_window()
    wait = WebDriverWait(driver,10)
    chain = ActionChains(driver)

    # Click on Log-In
    wait.until(EC.element_to_be_clickable(log_in_layer)).click()

    # Input your Detail
    u_d = (By.XPATH,"//input[@placeholder='Enter your active Email ID / Username']")
    wait.until(EC.visibility_of_element_located(u_d)).send_keys(user)
    wait.until(EC.visibility_of_element_located(password_details)).send_keys(passcode)
    wait.until(EC.element_to_be_clickable(log_in_click)).click()
    time.sleep(2)
    driver.get(list_urls[0])
    
    keyword_title = ["Data Analyst", "Data Scientist","Python","Machine Learning","Artificial Intelligence", "Data Science","Visusalization",
                    "Deep Learning","Natural Language","Computer Vision","Data Mining","Power BI", "Tableau","Data Analysis","Data Modeling",
                    "Data Wrangling","Business Analyst"]
    keyword_title2 = ["ML", "AI", "CV", "NLP","SQL"]
    not_keywords = ["Developer","Django","Stack","Config","Server","Admin","Associate","Content","Female"]
    
    job_link = []
    job_title = []
    
    i = 0
    while i < len(list_urls):
        jobs_wait = (By.XPATH, "//article")
        wait.until(EC.visibility_of_all_elements_located(jobs_wait))

        jobs = driver.find_elements(By.XPATH, "//article")

        for j in range(len(jobs)):
            job_posting = driver.find_element(By.XPATH, f'//article[{j+1}]/div[1]/div[1]/a[1]').text
            if (any(item.lower() in job_posting.lower() for item in keyword_title) or any(item in job_posting for item in keyword_title2)) and not any(item.lower() in job_posting.lower() for item in not_keywords):
                job_link.append(driver.find_element(By.XPATH, f'//article[{j+1}]/div[1]/div[1]/a[1]').get_attribute('href'))
                job_title.append(driver.find_element(By.XPATH, f'//article[{j+1}]/div[1]/div[1]/a[1]').text)
                
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='fright fs14 btn-secondary br2']"))).click()
        except Exception as e:
            print('No job further')
        i += 1
    driver.close()
    
    job_df = pd.DataFrame({'Title' : job_title, 'URL' : job_link})
    filename = list_urls[-1].split('?')[0].split('-')[-1]+'.csv'
    save_dir = r'C:\Users\Aditya\Desktop\Naukri\Large_Scrape'
    fp = os.path.join(save_dir,filename)
    job_df.to_csv(fp)

def splitted_list(iplist, num_parts):
    length = len(iplist)
    final = [iplist[j:j+num_parts] for j in range(0,length,num_parts)]
    return final

def parallel_scraping_large_scale(urls_lists):
    processes = []
    for ulist in urls_lists:
        process = multiprocessing.Process(target=get_df, args=('adi221800@gmail.com', '5zJV!&zCSw6pGdA', 'Data Sciecne', 4, ulist))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()

search_url_list = splitted_list(get_total_urls('adi221800@gmail.com', '5zJV!&zCSw6pGdA', 'Data Analyst', 3),500)

if __name__ == "__main__":
    parallel_scraping_large_scale(search_url_list)