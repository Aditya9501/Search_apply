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



def get_joblink_with_login(user,passcode,jobdesgn,yrsexp):
    driver = webdriver.Chrome()
    driver.get(naukri)
    driver.maximize_window()
    wait = WebDriverWait(driver,5)
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

    # Print Similar items
    simi_jobs = (By.XPATH,"//div[contains(@class,'nI-gNb-search-bar')]//li//div")
    wait.until(EC.visibility_of_all_elements_located(simi_jobs))
    similar = driver.find_elements(By.XPATH,"//div[contains(@class,'nI-gNb-search-bar')]//li//div")
    similar_list = [i.get_attribute('title') for i in similar]
    
    # Click on Search
    search_loc =(By.XPATH, "//span[normalize-space()='Search']")
    wait.until(EC.element_to_be_clickable(search_loc)).click()
    
    freshness = (By.XPATH,"//input[@id='filter-freshnessFor']")
    wait.until(EC.element_to_be_clickable(freshness)).click()
    wait.until(EC.element_to_be_clickable(freshness)).click()

    job_posted = (By.XPATH,"//div[@id='dp_filter-freshness'][1]//div/ul/li[5]")
    wait.until(EC.visibility_of_element_located(job_posted))
    chain.move_to_element(driver.find_element(By.XPATH,"//div[@id='dp_filter-freshness'][1]//div/ul/li[5]")).click().perform()
    
    wait.until(EC.element_to_be_clickable((By.XPATH,"//div[@class='inside']")))
    dragger=driver.find_element(By.XPATH,"//div[@class='inside']")
    chain.move_to_element(dragger).click_and_hold().pause(1).drag_and_drop_by_offset(dragger,(((yrsexp)*7)-210),0).perform()

    listing_xpath = "(/html[1]/body[1]/div[1]/div[4]/div[1]/div[1]/section[2]/div[1]/div[1]/span[1])|(/html[1]/body[1]/div[1]/div[5]/div[2]/div[1]/section[2]/div[1]/div[1]/span[1])"
    listings = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,listing_xpath)))
    total_listing = listings.text
    pages = int(int(total_listing.split(" ")[-1])/(int(total_listing.split(' ')[2])))

    print(f'Total Job postings are {total_listing.split(" ")[-1]}')
    
    keyword_title = ["Data Analyst", "Data Scientist","Python","Machine Learning","Artificial Intelligence", "Data Science","Visusalization",
                    "Deep Learning","Natural Language","Computer Vision","Data Mining","Power BI", "Tableau","Data Analysis","Data Modeling",
                    "Data Wrangling","Business Analyst"]
    keyword_title2 = ["ML", "AI", "CV", "NLP","SQL"]
    not_keywords = ["Developer","Django","Stack","Config","Server","Admin","Associate","Content"]
    
    job_link = []
    job_title = []
    i = 0

    while i < pages:
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
    
    return job_df

def get_keyskill(user,passcode,df):
    main_skill = []
    main_skill1 = []
    url = naukri
    driver = webdriver.Chrome()
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver,5)
    wait = WebDriverWait(driver,10)

    wait.until(EC.element_to_be_clickable(log_in_layer)).click()

    # Input your Details
    u_d = (By.XPATH,"//input[@placeholder='Enter your active Email ID / Username']")
    wait.until(EC.visibility_of_element_located(u_d)).send_keys(user)
    wait.until(EC.visibility_of_element_located(password_details)).send_keys(passcode)
    wait.until(EC.element_to_be_clickable(log_in_click)).click()

    time.sleep(2)

    for joburl in df.URL.values:
        driver.get(joburl)
        dicti = {1: "div[contains(@class,'key-skill')]", 2: "div[contains(@class,'getJobKeySkillsSection key-skill')]", 3: "div[contains(@class,'styles_key-skill__GIPn_')]"}
        for loc in dicti:
            try:
                wait.until(EC.visibility_of_all_elements_located((By.XPATH, f"//{dicti[loc]}/div/a/span")))
                tot_skill = driver.find_elements(By.XPATH, f"//{dicti[loc]}/div/a/span")
                keyskills = [i.text for i in tot_skill]

                try:
                    if dicti[loc] == "div[contains(@class,'styles_key-skill__GIPn_')]":
                        highlighted = driver.find_elements(By.XPATH, f"//{dicti[loc]}/div/a/i")
                    else:
                        highlighted = driver.find_elements(By.XPATH, f"//{dicti[loc]}/div/a/em")
                    a = len(highlighted)
                except Exception as e:
                    a = 'all'

            except Exception as e:
                pass
            try:
                button = driver.find_element(By.XPATH, "//button[2]")
                main_skill.append((keyskills, a, button.text, joburl))
            except:
                main_skill.append((keyskills, a, "Not Possible", joburl))
    
            main_skill1 = [main_skill[i] for i in range(0,len(main_skill),3)]
        
    apply_df = pd.DataFrame(main_skill1)
    apply_df.columns = ['Skills','Highlighted','Response','URL']
    apply_df = pd.merge(left=df,right=apply_df,on='URL',how='inner')
    return apply_df

def autoapply(user,passcode,jobdesgn,yrsexp):
    
    job_df = get_joblink_with_login(user,passcode,jobdesgn,yrsexp)
    print(f'keyskill to serach from {len(job_df.URL.values)} jobs')
    
    apply_df = get_keyskill(user,passcode,job_df)
    apply_df = apply_df[~apply_df["URL"].duplicated()]    
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%d%m%y_%I%M%p")

    filename = formatted_datetime+'_'+jobdesgn+'.csv'
    path = r'C:\Users\Aditya\Desktop\Naukri\Search_Apply'
    apply_df.to_csv(os.path.join(path,filename),index=False)

    # now_apply = apply_df['URL'][apply_df['Response']=='Apply'].values
    
    # print(f'We can appply to {len(now_apply)} jobs')

    # driver = webdriver.Chrome()
    # driver.get(naukri)
    # driver.maximize_window()

    # wait = WebDriverWait(driver,5)

    # wait.until(EC.element_to_be_clickable(log_in_layer)).click()

    # # Input your Details
    # u_d = (By.XPATH,"//input[@placeholder='Enter your active Email ID / Username']")
    # wait.until(EC.visibility_of_element_located(u_d)).send_keys(user)
    # wait.until(EC.visibility_of_element_located(password_details)).send_keys(passcode)
    # wait.until(EC.element_to_be_clickable(log_in_click)).click()

    # time.sleep(2)

    # for joburl in now_apply:
    #     driver.get(joburl)
    #     try:
    #         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, applied_button)))
    #         print('Already Applied to the job')
    #     except:
    #         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, to_apply_button))).click()

    # driver.quit()

autoapply('adi221800@gmail.com','5zJV!&zCSw6pGdA','AI', 3)
