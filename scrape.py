import json
import time
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import lxml.html




def fetch(term, dept ="", type = ""):
    print("Finding courses...")
    # Connect to the page to clear past searches
    browser.get('https://cdcs.ur.rochester.edu/')
    print(time.strftime("%H:%M:%S",  time.localtime()), "    -Webpage connected")


    # Enter info into the form

    Select(browser.find_element(By.ID, 'ddlTerm')).select_by_value(term)    # REQUIRED

    Select(browser.find_element(By.ID, 'ddlDept')).select_by_value(dept)
    Select(browser.find_element(By.ID, 'ddlTypes')).select_by_visible_text("Lecture")
    # Select(browser.find_element(By.ID, 'ddlDept')).select_by_value(type)
    (browser.find_element(By.ID, 'txtCourse')).send_keys("CSC 172")

    # Submit the form
    browser.find_element(By.ID, 'btnSearchTop').click()
    start_time = time.localtime()
    print(time.strftime("%H:%M:%S", start_time), "    -Form submitted")


    
    browser.get_screenshot_as_file('sample_screenshot_2.png')
    
    # Recieve HTML info about the classes
    tables = browser.find_elements(By.XPATH, '//table[contains(@cellpadding, "3")]')

    
    # Check for timeout issues
    end_time = time.localtime()
    diff = (time.mktime(end_time) - time.mktime(start_time)) 

    if(diff >= sleepTime and len(tables) == 0):
        print(time.strftime("%H:%M:%S",end_time), " -Timeout error occured")
        browser.get_screenshot_as_file('timeout_screenshot.png')
        return None


    elif len(tables) == 0:  
        return None
        
    else:   # Parse the gathered data
        print(time.strftime("%H:%M:%S",end_time), "    -Results found (", str(len(tables)) , ")")
    
        lookup = []
        browser.implicitly_wait(0.001)

        root = lxml.html.fromstring(browser.page_source)
        
        for table in root.xpath('//table[contains(@cellpadding, "3")]'):
            # tableID = "/html/body/form/div[3]/table[1]/tbody/tr[2]/td[2]/div/table/tbody/tr/td[3]/table[" + str(i) + "]/tbody/"
            # for x in range(1, 10,2 ): #len(tables)
            dict = {"Title": "",
                "Days": "",
                "Term": "",
                "Credit": "",
                "Open": False,
                "Start": "",
                "End": "",
                "Room": "",
                "Capacity": "",
                "Enrolled": "",
                "Instructor": "",
                "Description": "",
                "Restrictions": [],
                "Offered": "",
                "Showing": True}

            # dict = {"Title": browser.find_element(By.XPATH, tableID  + "tr[3]/td[1]").text + " " + browser.find_element(By.XPATH, tableID  + "tr[3]/td[2]").text,
            # "Days": browser.find_element(By.XPATH,tableID  + "tr[4]/td[2]/table[2]/tbody/tr/td[1]").text,
            # "Term": browser.find_element(By.XPATH, tableID  + "tr[3]/td[3]").text,
            # "Credit": browser.find_element(By.XPATH, tableID  + "tr[3]/td[4]").text,    #make sure this is fixed for workshops
            # "Open": "Open" == browser.find_element(By.XPATH, tableID  + "tr[3]/td[5]").text,
            # "Start": browser.find_element(By.XPATH,tableID  + "tr[4]/td[2]/table[2]/tbody/tr/td[2]").text,
            # "End": browser.find_element(By.XPATH,tableID  + "tr[4]/td[2]/table[2]/tbody/tr/td[3]").text,
            # "Room": browser.find_element(By.XPATH,tableID  + "tr[4]/td[2]/table[2]/tbody/tr/td[4]").text,
            # "Capacity": browser.find_element(By.XPATH,tableID  + "tr[5]/td[" + str(3) + "]/span").text,
            # "Enrolled": browser.find_element(By.XPATH,tableID  + "tr[5]/td[" + str(2) + "]/span").text,
            # "Instructor": browser.find_element(By.XPATH,tableID  + "tr[6]/td[2]/span").text,
            # "Description": browser.find_element(By.XPATH,tableID  + "tr[7]/td[2]/span").text,
            # "Restrictions": [],
            # "Offered": browser.find_element(By.XPATH,tableID  + "tr[8]/td[2]/span").text.split(" "),
            # "Showing": True}

            # print(table.xpath(".//span[contains(@id,'lblCNum')]/text()"))

            # print(table.cssselect("span.lblName").text_content())
            try:
                dict["Title"] = table.xpath(".//span[contains(@id,'lblCNum')]/text()")[0] + " " + table.xpath(".//span[contains(@id,'lblTitle')]/text()")[0]
            except:
                pass
            
            try:
                dict["Days"] =  table.xpath(".//span[contains(@id,'lblDay')]/text()")[0]
            except:
                pass


            try:
                dict["Term"] =  table.xpath(".//span[contains(@id,'lblTerm')]/text()")[0]
                
            except:
                pass

            try:
                dict["Credit"] = table.xpath(".//span[contains(@id,'lblCredits')]/text()")[0]       
                
            except:
                pass

            try:
                dict["Open"] = "Open" == table.xpath(".//span[contains(@id,'lblStatus')]/text()")[0]
            except:
                pass

            try:
                dict["Start"] = table.xpath(".//span[contains(@id,'lblStartTime')]/text()")[0]
            except:
                pass

            try:
                dict["End"] =  table.xpath(".//span[contains(@id,'lblEndTime')]/text()")[0]
            except:
                pass

            try:
                dict["Room"] =  table.xpath(".//span[contains(@id,'lblBuilding')]/text()")[0]
            except:
                pass

            try:
                dict["Capacity"] =table.xpath(".//span[contains(@id,'lblSectionCap')]/text()")[0]
            except:
                pass

            try:
                dict["Enrolled"] =  table.xpath(".//span[contains(@id,'lblSectionEnroll')]/text()")[0]
            except:
                pass

            try:
                dict["Instructor"] =  table.xpath(".//span[contains(@id,'lblInstructors')]/text()")[0]
            except:
                pass

            try:
        
                for children in table.xpath(".//span[contains(@id,'lblDesc')]"):
                     for x in children.itertext():
                         dict["Description"] += x + "\n"
                         print(x)
            except:
                pass

            try:
                dict["Offered"] = table.xpath(".//span[contains(@id,'lblOffered')]/text()")[0].split(" ")

                if "" in dict["Offered"]:
                    dict["Offered"].remove("")
            except:
                pass

            lookup.append(dict)
        return lookup
            # try:
            #     dict["Title"] = table.find_element(By.CSS_SELECTOR, "span[id$='lblCNum']").text  + " " + tables[i].find_element(By.CSS_SELECTOR, "span[id$='lblTitle']").text 
            # except:
            #     pass
            
            # try:
            #     dict["Days"] = table.xpath('.//tr[4]/td[2]/table[2]/tbody/tr/td[1]/span/text()')
                
                
            #     # .find_element(By.CSS_SELECTOR, "span[id$='lblDay']").text 
            # except:
            #     pass


            # try:
            #     dict["Term"] =  table.find_element(By.CSS_SELECTOR, "span[id$='lblTerm']").text 
                
            # except:
            #     pass

            # try:
            #     dict["Credit"] = table.find_element(By.CSS_SELECTOR, "span[id$='lblCredits']").text 
                
            # except:
            #     pass

            # try:
            #     dict["Open"] = "Open" == table.find_element(By.CSS_SELECTOR, "span[id$='lblStatus']").text 
            # except:
            #     pass

            # try:
            #     dict["Start"] = table.find_element(By.CSS_SELECTOR, "span[id$='lblStartTime']").text 
            # except:
            #     pass

            # try:
            #     dict["End"] =  table.find_element(By.CSS_SELECTOR, "span[id$='lblEndTime']").text 
            # except:
            #     pass

            # try:
            #     dict["Room"] =  table.find_element(By.CSS_SELECTOR, "span[id$='lblBuilding']").text 
            # except:
            #     pass

            # try:
            #     dict["Capacity"] = table.find_element(By.CSS_SELECTOR, "span[id$='lblSectionCap']").text 
            # except:
            #     pass

            # try:
            #     dict["Enrolled"] =  table.find_element(By.CSS_SELECTOR, "span[id$='lblSectionEnroll']").text 
            # except:
            #     pass

            # try:
            #     dict["Instructor"] =  table.find_element(By.CSS_SELECTOR, "span[id$='lblInstructors']").text 
            # except:
            #     pass

            # try:
            #     dict["Description"] = table.find_element(By.CSS_SELECTOR, "span[id$='lblDesc']").text 
            # except:
            #     pass

            # try:
            #     dict["Offered"] = table.find_element(By.CSS_SELECTOR, "span[id$='lblOffered']").text.split()
            # except:
            #     pass



                

                # FIXME this is still slower...

                # print(browser.find_element(By.XPATH, tableID  + "tr[3]/td[1]").text)
                # print(browser.find_element(By.XPATH, tableID  + "tr[3]/td[2]").text)
                # print(browser.find_element(By.XPATH, tableID  + "tr[3]/td[3]").text)
                # # print(browser.find_element(By.XPATH, tableID  + "tr[3]/td[4]").text)
                # print(browser.find_element(By.XPATH, tableID  + "tr[3]/td[5]").text)


                
                # # print(browser.find_element(By.XPATH,tableID  + "tr[4]/td[2]/table[2]/tbody/tr/td[1]").text)
                # print(browser.find_element(By.XPATH,tableID  + "tr[4]/td[2]/table[2]/tbody/tr/td[2]").text)
                # print(browser.find_element(By.XPATH,tableID  + "tr[4]/td[2]/table[2]/tbody/tr/td[3]").text)
                # print(browser.find_element(By.XPATH,tableID  + "tr[4]/td[2]/table[2]/tbody/tr/td[4]").text)


                # print(browser.find_element(By.XPATH,tableID  + "tr[5]/td[" + str(2) + "]/span").text)
                # print(browser.find_element(By.XPATH,tableID  + "tr[5]/td[" + str(3) + "]/span").text)

                # print(browser.find_element(By.XPATH,tableID  + "tr[6]/td[2]/span").text)


                # print(browser.find_element(By.XPATH,tableID  + "tr[7]/td[2]/span").text)

                # print(browser.find_element(By.XPATH,tableID  + "tr[8]/td[2]/span").text)

                # For restrictions, but xpath is broken
                # uv = browser.find_elements(By.XPATH,"/html/body/form/div[3]/table[1]/tbody/tr[2]/td[2]/div/table/tbody/tr/td[3]/table[3]/tbody/tr[7]/td[2]/span/p")

                # print(len(uv))
                # for paragraph in uv:
                #     print(paragraph.text)

                




                # entry = tables[x].text.split('\n')
                # Corner case for first class
                # if('Arts, Sciences, and Engineering Computer Science' in entry):
                #     entry.remove('Arts, Sciences, and Engineering Computer Science')


                
            # lookup.append(make_course(x))

            # Print the finishing time
            


        


def get_dropbox_info():
    print("Finding dropbox info...")

    browser.get('https://cdcs.ur.rochester.edu/')
    print(time.strftime("%H:%M:%S",  time.localtime()), "    -Webpage connected")

    term_menu = []
    term_option = []
    for option in Select(browser.find_element(By.ID, 'ddlTerm')).options:
        term_menu.append(option.text)
        term_option.append(option.get_attribute('value'))



    dept_menu = []
    dept_option = []
    for option in Select(browser.find_element(By.ID, 'ddlDept')).options:
        dept_menu.append(option.text)
        dept_option.append( option.get_attribute('value'))



    type_menu = []
    type_option = []
    for option in Select(browser.find_element(By.ID, 'ddlTypes')).options:
        type_menu.append(option.text)
        type_option.append(option.get_attribute('value'))

    print(time.strftime("%H:%M:%S",time.localtime()), "    -Dropbox info recorded")

    return {"Term" : [term_menu, term_option], "Dept" : [dept_menu, dept_option], "Type" : [type_menu, type_option]}




def dropbox_2():
    browser.get('https://cdcs.ur.rochester.edu/')

    root = lxml.html.fromstring(browser.page_source)
    term_option = (root.xpath('//*[@id="ddlTerm"]/option/text()'))
    dept_option = (root.xpath('//*[@id="ddlDept"]/option/text()'))
    type_option = (root.xpath('//*[@id="ddlTypes"]/option/text()'))

    return  [term_option, dept_option, type_option]

    
 


# Turn the HTML data into a dictionary for each course
def make_course(data):

    
    dict = {"Title": "",
            "Days": "",
            "Term": "",
            "Credit": "",
            "Open": False,
            "Start": "",
            "End": "",
            "Room": "",
            "Capacity": "",
            "Enrolled": "",
            "Instructor": "",
            "Description": "",
            "Restrictions": [],
            "Offered": "",
            "Showing": True}
    
    dict =["","","","",False,"","","","","","",[],"",True]
    
    tmp = data[1].split(" ")
    dict["Term"] = tmp[-4] + " " +  tmp[-3]
    dict["Credit"] = tmp[-2]
    dict["Open"] = tmp[-1] == "Open"
    
    if tmp[-6] == "-":
        dict["Credit"] = tmp[-5]
        for i in range(0,len(tmp) - 6):
            dict["Title"] = dict["Title"] + " " +tmp[i]
    else: 
        for i in range(0,len(tmp) - 4):
            dict["Title"] = dict["Title"] + " " +tmp[i]


    for item in data[2:-1]:
        if ("Day Begin End Location Start Date End Date") in item:
            if  not ("Enrollment") in data[data.index(item) + 1]:
                items = data[data.index(item) + 1].split(" ")
                dict["Days"] = list(items[0])
                dict["Start"] = int(items[1])
                dict["End"] = int(items[2])

                for r in items[3:-2]:
                    dict["Room"] = dict["Room"] + " " + r
                    
        if ("Capacity") in item:
            dict["Enrolled"] = item[0:item.index(" ")]
            dict["Capacity"] = data[data.index(item) + 1]

        if ("Instructors") in item:
            dict["Instructor"] = item[12:]

        if ("Description") in item:
            dict["Description"] = item[12:]

        if ("Offered") in item:
            dict["Offered"] = item[9:].split(" ")

    


    

   

    return dict




#  Maybe alter so you don't need to establish a connection every time
sleepTime = 120


# Print initial time
print(time.strftime("%H:%M:%S", time.localtime()), "    -Searching for webpage")


# Set up broeser connection
options = Options()
options.add_argument("--headless")
browser = webdriver.Firefox(options=options)
browser.implicitly_wait(sleepTime)

# dropbox_info = get_dropbox_info()

# # Test two searches
# results = fetch('D-Spring 2023', dept='CSC')

dropbox_2()

print(time.strftime("%H:%M:%S", time.localtime()), "    -Results parsed")


# for res in results:

#     print(res )
#     print("\n\n")



# tables = fetch('D-Spring 2023', 'MATH')
# tables = fetch('D-Spring 2023', 'CSC')

# # Exit and save data to a JSON file
# browser.close()


# out = open("scraped_classes.json", "w")
# json_out_data = json.dumps(results)
# out.write(json_out_data)
# out.close()


# out = open("dropbox_info.json", "w")
# json_out_data = json.dumps(dropbox_info)
# out.write(json_out_data)
# out.close()
