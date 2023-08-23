from selenium import webdriver
import pandas as pd
import time
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_joblink_with_login(user,passcode,jobdesgn,yrsexp):
    driver = webdriver.Chrome()
    driver.get("https://www.naukri.com")
    driver.maximize_window()

    wait = WebDriverWait(driver,10)
    chain = ActionChains(driver)

    # Click on Log-In
    log_in_layer = (By.XPATH,"//a[@id='login_Layer']")
    wait.until(EC.element_to_be_clickable(log_in_layer)).click()

    # Input your Detail
    username_deatails = (By.XPATH,"//input[@placeholder='Enter your active Email ID / Username']")
    password_details = (By.XPATH, "//input[@placeholder='Enter your password']")
    log_in_click = (By.XPATH,"//button[@type='submit']")

    wait.until(EC.visibility_of_element_located(username_deatails)).send_keys(user)
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

    wait.until(EC.visibility_of_element_located((By.XPATH, "/html[1]/body[1]/div[1]/div[4]/div[1]/div[1]/section[2]/div[1]/div[1]/span[1]")))
    total_listing = driver.find_element(By.XPATH, "/html[1]/body[1]/div[1]/div[4]/div[1]/div[1]/section[2]/div[1]/div[1]/span[1]").text
    pages = int(int(total_listing.split(" ")[-1])/(int(total_listing.split(' ')[2])))

    print(f'Total Job postings are {total_listing.split(" ")[-1]}')
    
    keyword_title = ["Data Analyst", "Data Scientist","Python","Machine Learning","Artificial Intelligence", "Data Science","Visusalization",
                    "Deep Learning","Natural Language","Computer Vision","Data Mining","Power BI", "Tableau","Data Analysis","Data Modeling",
                    "Data Wrangling","Business Analyst"]
    keyword_title2 = ["ML", "AI", "CV", "NLP","SQL"]
    not_keywords = ["Developer","Django","Stack","Config","Server","Admin"]
    
    job_link = []
    job_title = []
    i = 0

    while i < pages:
        jobs_wait = (By.XPATH, "//article")
        wait.until(EC.visibility_of_all_elements_located(jobs_wait))

        jobs = driver.find_elements(By.XPATH, "//article")

        for j in range(len(jobs)):
            Title = driver.find_element(By.XPATH, f'//article[{j+1}]/div[1]/div[1]/a[1]').text
            if (any(item.lower() in Title.lower() for item in keyword_title) or any(item in Title for item in keyword_title2)) and not any(item.lower() in Title.lower() for item in not_keywords):
                job_link.append(driver.find_element(By.XPATH, f'//article[{j+1}]/div[1]/div[1]/a[1]').get_attribute('href'))
                job_title.append(driver.find_element(By.XPATH, f'//article[{j+1}]/div[1]/div[1]/a[1]').text)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='fright fs14 btn-secondary br2']"))).click()

        i += 1
    driver.close()

    job_df = pd.DataFrame({'Title' : job_title, 'URL' : job_link})
    
    return job_df

def get_keyskill_up(user,passcode,df):
    main_skill = []
    url = "https://www.naukri.com"
    driver = webdriver.Chrome()
    driver.get(url)
    driver.maximize_window()

    wait = WebDriverWait(driver,10)

    log_in_layer = (By.XPATH, "//a[@id='login_Layer']")
    wait.until(EC.element_to_be_clickable(log_in_layer)).click()

    # Input your Details
    username_details = (By.XPATH, "//input[@placeholder='Enter your active Email ID / Username']")
    password_details = (By.XPATH, "//input[@placeholder='Enter your password']")
    log_in_click = (By.XPATH, "//button[@type='submit']")

    wait.until(EC.visibility_of_element_located(username_details)).send_keys(user)
    wait.until(EC.visibility_of_element_located(password_details)).send_keys(passcode)
    wait.until(EC.element_to_be_clickable(log_in_click)).click()

    time.sleep(2)
    
    for joburl in df.URL.values:
        driver.get(joburl)
    
        try:
            wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='getJobKeySkillsSection key-skill']/div/a/span")))
            tot_skill = driver.find_elements(By.XPATH, "//div[@class='getJobKeySkillsSection key-skill']/div/a/span")
            keyskills = [i.text for i in tot_skill]

            try:
                highlighted = driver.find_elements(By.XPATH, "//div[@class='getJobKeySkillsSection key-skill']/div/a/em")
                a = len(highlighted)
            except Exception as e:
                a = 'all'

            main_skill.append((keyskills, a, "Not Possible",joburl))

        except TimeoutException as e1:
            try:
                wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='key-skill']/div/a/span")))
                tot_skill = driver.find_elements(By.XPATH, "//div[@class='key-skill']/div/a/span")
                keyskills = [i.text for i in tot_skill]

                try:
                    highlighted = driver.find_elements(By.XPATH, "//div[@class='key-skill']/div/a/em")
                    a = len(highlighted)
                except Exception as e:
                    a = 'all'
                
                button = driver.find_element(By.XPATH, "//button[2]")
                main_skill.append((keyskills, a, button.text,joburl))
#                 try:
#                     button = driver.find_element(By.XPATH, "//button[2]")
#                 except Exception as e:
#                     button = None

#                 if button:
#                     main_skill.append((keyskills, a, button.text,joburl))
#                 else:
#                     main_skill.append((keyskills, a))

            except TimeoutException as e2:
                try:
                    wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='styles_key-skill__GIPn_']/div/a/span")))
                    tot_skill = driver.find_elements(By.XPATH, "//div[@class='styles_key-skill__GIPn_']/div/a/span")
                    keyskills = [i.text for i in tot_skill]

                    try:
                        highlighted = driver.find_elements(By.XPATH, "//div[@class='styles_key-skill__GIPn_']/div/a/i")
                        a = len(highlighted)
                    except Exception as e:
                        a = 'all'

                    button = driver.find_element(By.XPATH, "//button[2]")
                    main_skill.append((keyskills, a, button.text,joburl))
#                     try:
#                         button = driver.find_element(By.XPATH, "//button[2]")
#                     except Exception as e:
#                         button = None

#                     if button:
#                         main_skill.append((keyskills, a, button.text))
#                     else:
#                         main_skill.append((keyskills, a))

                except TimeoutException as e3:
                    main_skill.append(('keyskills', 'a', 'button.text'))  # No need to print here since the visibility print statements are removed

        finally:
            pass
    apply_df = pd.DataFrame(main_skill)
    apply_df.columns = ['Skills','Highlighted','Response','URL']
    apply_df = pd.merge(left=df,right=apply_df,on='URL',how='inner')
    return apply_df

print(get_keyskill_up('adi221800@gmail.com','5zJV!&zCSw6pGdA',get_joblink_with_login('adi221800@gmail.com','5zJV!&zCSw6pGdA','Data Science',2)))