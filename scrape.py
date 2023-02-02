import time
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def fetch(term, dept, sleepTime):
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Firefox(options=options)

    browser.get('https://cdcs.ur.rochester.edu/')
    Select(browser.find_element(By.ID, 'ddlTerm')).select_by_value(term)
    Select(browser.find_element(By.ID, 'ddlDept')).select_by_value(dept)

    browser.find_element(By.ID, 'btnSearchTop').click()

    print('Sleeping for ', sleepTime)
    time.sleep(sleepTime)
    browser.get_screenshot_as_file('sample_screenshot_2.png')
    return browser


try:

    browser = fetch('D-Spring 2023', 'CSC', 15)
    tables = browser.find_elements(By.XPATH, '//table[contains(@cellpadding, "3")]')

    # print(browser.find_element(By.ID, 'rpResults_ctl01_lblSchool'))
    # tables = browser.find_elements(By.XPATH, '//td[contains(@id, "rpResults_ct")]')
    # tables = browser.find_elements(By.XPATH, '//span[contains(@id, "rpResults_ct")]')

    print(len(tables))
    #tables.pop(0)

    # to get the header with text method
    # tds = tables[0].find_elements(By.TAG_NAME, 'td')

    classes = []
    dict = {}

    for x in range(0, len(tables)):
       # print('     ',j)
        i = tables[x]

        e = i.text.split('\n')
        # Corner case for first class
        if(e.__contains__('Arts, Sciences, and Engineering Computer Science')):
            e.remove('Arts, Sciences, and Engineering Computer Science')

        e.remove('Course Course Title Term Credits Status')
        e.remove('Schedule:')
        e.remove('Enrollment: Enrolled     ')
        e.remove('Day Begin End Location Start Date End Date')
        e.remove('Books Click to buy books for this course from the bookstore')
      #  print(e)
        classes.append(e)

        #print(e[0][0:10])
        dict[e[0][0:10]] = e
       # print()

    for k in dict:
        print(dict[k])
    

   # print(browser.page_source)

finally:
    try:
        browser.close()
    except:
        pass
