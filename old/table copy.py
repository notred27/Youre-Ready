import json
from tkinter import*
from tkinter import ttk
import tkinter
import json
import time
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import threading
import lxml.html
import customtkinter

#TODO: fix minor errors,  restrictions scraping (addig bold to this text), class type scraping, red tint if filled/ unavailable class, 
#  dropdown menues for selected courses, add graphical 
# elements when searching for quereys / no results are found

# Add a check that if someone signs up for a workshop, they also sign up for the lecture (dropdown menu for workshop classes from main lecture class?)


# Known errors: FUNCTION REDUNDANCY, errors with connecting to CDCS & exiting connection on program close, 
#  scroll pane doesn't work unless over the bar (scrolling on the
# individual frames instead), setting scroll bar location after a search, finding what hight the course panes should 
# be according to the wrapped text, errors with UI element placing and consistancy, hide PREV and NEXT buttons on 
# page for selected courses, error when scraping credits that "Wrokshop" isn't recognized or set up correctly in the scraper

# Update dynamic scroll bar resizing

# Bug with scroll bar not showing up


# def dropbox_2():
#     browser.get('https://cdcs.ur.rochester.edu/')

#     root = lxml.html.fromstring(browser.page_source)
#     term_option = (root.xpath('//*[@id="ddlTerm"]/option/text()'))
#     dept_option = (root.xpath('//*[@id="ddlDept"]/option/text()'))
#     type_option = (root.xpath('//*[@id="ddlTypes"]/option/text()'))

#     return  [term_option, dept_option, type_option]



loadData = []  # json.loads(open("scraped_classes.json", "r").read())
# load_dropbox = dropbox_2()

current_classes = json.loads(open("saved_classes.json", "r").read())

days = ["M", "T", "W","R","F", ""]


# Indexes for shown results
indxS= 1
indxE = 0
numResults = len(loadData)

sleepTime = 60  #For timeout checks


# Print initial time
print(time.strftime("%H:%M:%S", time.localtime()), "    -Searching for webpage")


# Set up browser connection     FIXME
options = Options()
options.add_argument("--headless")
browser = webdriver.Firefox(options=options)
browser.implicitly_wait(sleepTime)

def time_to_str(time):
    if type(time) is int:
        if time > 1300:
            time -= 1200
        
        time = str(time)
        

        time = time[:-2] + ":" + time[-2:]
        return time
    return ""

def make_text(parent, dict):
    text = customtkinter.CTkLabel(parent, width = 500, height = 1, text= dict["Title"], font=customtkinter.CTkFont(size=15, weight="bold"), fg_color="transparent")

    text.pack(pady=(10,0))


    text = customtkinter.CTkTextbox(parent, width = 500,height = 120,  font=customtkinter.CTkFont(size=12, weight="normal"), spacing1=5, wrap=WORD, fg_color="transparent")
    text.insert("end", str("".join(dict["Days"])) + ": " + time_to_str(dict["Start"]) + "-" + time_to_str(dict["End"]) + "     Credit: " + dict["Credit"]  
                + "     Term: " + dict["Term"] + "\nInstructor: " +  dict["Instructor"] + "\nRoom: "+ dict["Room"] + "\nEnrolled: " + dict["Enrolled"] + '/' + dict["Capacity"] + "\nOffered: " +  ", ".join(dict["Offered"])) 
    text.configure(state="disabled")
    text.pack()

    
    text = customtkinter.CTkTextbox(parent, width = 500, font=customtkinter.CTkFont(size=10, weight="normal"), spacing1=5, wrap=WORD, fg_color="transparent")
    text.insert("end", dict["Description"] ) 
    
    # print((int(text.index('end').split('.')[0]) - 1) * 2 + 1)
    text.configure(state="disabled")
    text.configure(height=((int(text.index('end-1c').split('.')[0])) * 4 + 1) * 10 + 20)    #TODO very janky, find proper method
    text.pack()


    

def create_class_pane(dict):
    global classParent
    f=customtkinter.CTkFrame(classParent)
    make_text(f,dict)
    customtkinter.CTkButton(f, text="Add to Schedule", height = 1, command=lambda *args: add_course(dict)).pack(side = BOTTOM, anchor="se", padx = 4, pady = 4)
    f.pack(pady = 5)
   

#FIXME find out how to use tags to easily locate panes for different courses
def added_class_pane(dict):
    f=customtkinter.CTkFrame(selectedParent, height = 400)
    make_text(f,dict)
    customtkinter.CTkButton(f, text="Remove from Schedule", command=lambda *args: remove_course(dict, f)).pack(side = RIGHT, anchor="se", padx = 4, pady = 4)

    var = tkinter.IntVar()
    var.set(int(not dict["Showing"]))
    customtkinter.CTkCheckBox(f, text = "Hide Class", variable=var, command=lambda *args: toggle_show(dict, var)).pack( side =LEFT,  anchor="sw", padx = 4, pady = 4)    
    f.pack(pady = 5, padx = 0)

    toggle_show(dict, var)
    

def toggle_show(course, var):   #Intermediate function to work with IntVar so courses can be serialized using json
    #FIXME add color changes to pane here (and maybe add_class_pane) so they update when classes are changed
    if var.get() == 0:
        course["Showing"] = True
    else:
        course["Showing"] = False
        # change_wiget_color("#c7cdd6", selectedParent.nametowidget(course["Title"].lower()))
        
    # update_overlap()   FIXME
    draw_cal()

def update_overlap():       #FIXME update so that this also controls the colors of the classes on the clander from draw_cal() method?
    for course in current_classes:
        if course["Showing"]:
            try:
                change_wiget_color("white", selectedParent.nametowidget(course["Title"].lower()))
            except:
                pass

    for course in current_classes:
        if course["Showing"]:
            
            for day in course["Days"]:
                for other in current_classes:
                    if not other == course and day in other["Days"] and other["Showing"] and ((other["Start"] <= course["Start"] and course["Start"] <= other["End"]) or (course["Start"] <= other["Start"] and other["Start"] <= course["End"])):
                        overlap = True
                        #TODO send out a notif to other panes that they are overlapped
                        try:
                            change_wiget_color("#ffc2cc", selectedParent.nametowidget(other["Title"].lower()))
                        except:
                            pass

def change_wiget_color(color, widget):
    widget["bg"] = color

    for child in widget.winfo_children():
        if child.winfo_children():
            # child has children, go through its children
            change_wiget_color(color, child)
        elif type(child) is Label:
            child["bg"] = color

        elif type(child) is Frame:
            child["bg"] = color

        elif type(child) is Text:
            child["bg"] = color
        else:
            pass

def add_course(course):
    if course not in current_classes:
        current_classes.append(course)
        added_class_pane(course)
        for day in course["Days"]:
            add_class( day, " ".join(course["Title"].split(" ")[0:3]), course["Start"], color = "red")
        print(len(current_classes))

def remove_course(course, frame):
    global plan, num_credits_label, num_classes_label
    if(course in current_classes):
        current_classes.remove(course)
        frame.destroy()
    draw_cal()
    print(len(current_classes))


#TODO fix so elements get deleted with tags instead of having to redraw the entire canvas
def draw_cal(): #  Draw the background for the calender
    global num_credits_label, num_classes_label,canvas_num_courses,canvas_num_credits,classParent
    plan.delete('all')


    plan.create_line(414,20,14 +  400,580)
    for i in range(0,5):
        x = 14 +  i * 80
        plan.create_line(x,20,x,580)
        plan.create_text(x + 40,10, text=days[i])

    hours = ["", "8", "9","10","11", "12", "1", "2", "3","4","5", "6", "7","8", ""]
    for i in range(0,15):
        x = 20 +  i * 40
        plan.create_line(14,x,415,x, fill = 'grey')
        plan.create_text(6,x, text= hours[i], anchor = "center")

    num_credits_label = 0
    num_classes_label = 0
    for course in current_classes:
        if course["Showing"]:
            num_classes_label += 1
            try:
                num_credits_label += float(course["Credit"])
            except:
                pass
    
            overlap = False
            for day in course["Days"]:
                for other in current_classes:
                    if not other == course and day in other["Days"] and other["Showing"] and ((other["Start"] <= course["Start"] and course["Start"] <= other["End"]) or (course["Start"] <= other["Start"] and other["Start"] <= course["End"])):
                        overlap = True

            for day in course["Days"]:
                # TODO maybe change background pane to pink for classes that are overlapping?
                if overlap:
                    add_class(day, " ".join(course["Title"].split(" ")[0:2]), course["Start"], color = "red")
                else:
                    add_class(day, " ".join(course["Title"].split(" ")[0:2]), course["Start"], color = "blue")


    canvas_num_courses._text = "Number of Classes Chosen: " + str(num_classes_label)

    

    if int(num_credits_label) >= 20:
        canvas_num_credits['text'] = "Number of Credits Chosen: " + str(num_credits_label) + " (OVERLOAD)"
        # canvas_num_credits._fg_color= "red"      
    else:
        print(num_credits_label) #FIXME course labels not updating
        canvas_num_credits['text'] = "Number of Credits Chosen: " + str(num_credits_label)
        # canvas_num_credits = "white"
    
    


def add_class(day = "", title = "", timeStart = 0, length = 115, color = "blue"):   #Add a block to the calender
    time = timeStart - 700
    rem = time % 100
    y = (time // 100) * 40 + ((rem / 60) * 40) + 20
    x = 14 +  days.index(day) * 80
    lengthOff = (length // 100) * 40 + ((length % 100 / 60) * 40)

    # Time formating (from 24:00 TO AM/PM)
    if ((timeStart + length) % 100) >=  60:
        length = length - 60 + 100

    if(timeStart >= 1300):
        timeStart = timeStart - 1200

    if(timeStart + length >= 1300):
        length = length - 1200

    timeStr = str(timeStart // 100) + ":" 
    if(timeStart % 100) >=10:
        timeStr = timeStr + str(timeStart % 100) + " - " + str((timeStart + length) // 100) + ":"
    else:
        timeStr = timeStr + "0" + str(timeStart % 100) + " - " + str((timeStart + length) // 100) + ":"
        
    if(timeStart + length) % 100 >= 10:
        timeStr = timeStr + str((timeStart + length) % 100 )
    else:
        timeStr = timeStr + "0" +  str((timeStart + length) % 100 )

    
    plan.create_rectangle(x + 10,y,x + 70,y + lengthOff, fill = color, width = 0)
    plan.create_rectangle(x ,y + 10 ,x + 80,y + lengthOff - 10, fill = color, width = 0)

    plan.create_aa_circle(x+10, y+10, 10, fill = color) # top left
    plan.create_aa_circle(x+70, y+10, 10, fill = color) # top right

    plan.create_aa_circle(x+10, y + lengthOff-10, 10, fill = color) # bot left
    plan.create_aa_circle(x+70, y + lengthOff-10, 10, fill = color) # bot right



    plan.create_text(x + 6, y + 4, anchor="nw", text = title, fill  = 'white',font=customtkinter.CTkFont(size=12, weight="normal") )
    plan.create_text(x + 6, y + 18, anchor="nw", text = timeStr, fill  = 'white',font=customtkinter.CTkFont(size=10, weight="normal"))



# Functions for changing display on pages
def change_displayed_courses(startI, endI):
    global classParent
    # classParent.configure(height = 0)
    
    for child in classParent.winfo_children():
        child.destroy()

    for entry in range(startI-1,endI):
        create_class_pane(loadData[entry])              

    # canvas.create_window(0, 0, anchor='nw', window=classParent)
    # canvas.update_idletasks()

def next_page():
    global indxS, indxE
    if indxS + 50 <= numResults:
        indxS += 50
        indxE = min(indxS + 49, numResults)
        scroll_text['text'] = "Showing " + str(indxS) + "-" + str(indxE) + " of " + str(numResults)
        change_displayed_courses(indxS, indxE)


def prev_page():
    global indxS, indxE
    if indxS - 50 >= 1:
        indxS -= 50
        indxE = min(indxS + 49, numResults)
        scroll_text['text'] = "Showing " + str(indxS) + "-" + str(indxE) + " of " + str(numResults)
        change_displayed_courses(indxS, indxE)

def reset_page():
    global indxS, indxE, numResults

    indxS = 1
    indxE = min(50, len(loadData))
    numResults = len(loadData)
    
    scroll_text['text'] = "Showing " + str(indxS) + "-" + str(indxE) + " of " + str(numResults)
    
    change_displayed_courses(indxS, indxE)



def check_if_ready(thread):
    if thread.is_alive():
        # not ready yet, run the check again soon
        root.after(200, check_if_ready, thread)
    else:
        print("Thread has terminated, updating page")

        # try:    #FIXME jank logic for detecting if a timeout exception was thrown
        #     classParent.nametowidget("error_msg")
        # except:

        # if results_swap_btn._text ==  "Show Availible Courses":
        #     swap_panes()
        reset_page()


def fetch(term, dept ="", type = "", courseName = ""):

    # print(results_swap_btn._text)
    # if results_swap_btn._text ==  "Show Availible Courses":
    #         swap_panes()


    for c in classParent.winfo_children():
        c.destroy()

    textx = Label(classParent, text = "Searching for results...", font = ("helvetica", 20)).pack()

    courseName = courseSelect.get()
    desc = titleSelect.get()

    thread = threading.Thread(target=scrapeHTML, args=[term, dept, type,courseName,desc])
    thread.start()
    root.after(200, check_if_ready, thread)




def scrapeHTML(term, dept ="", type = "", courseName = "", desc = ""):
    global loadData
    print("Finding courses...")

    print(term, dept, type, courseName, desc)

    # Connect to the page to clear past searches
    browser.get('https://cdcs.ur.rochester.edu/')
    print(time.strftime("%H:%M:%S",  time.localtime()), "    -Webpage connected")

    # Enter info into the form
    Select(browser.find_element(By.ID, 'ddlTerm')).select_by_visible_text(term)    # REQUIRED
    Select(browser.find_element(By.ID, 'ddlDept')).select_by_visible_text(dept)
    Select(browser.find_element(By.ID, 'ddlTypes')).select_by_visible_text(type)

    if not courseName == "":
        (browser.find_element(By.ID, 'txtCourse')).send_keys(courseName)

    if not desc == "":
        (browser.find_element(By.ID, 'txtDescription')).send_keys(desc)

    # Submit the form
    browser.find_element(By.ID, 'btnSearchTop').click()
    start_time = time.localtime()
    print(time.strftime("%H:%M:%S", start_time), "    -Form submitted")
    
    # Recieve HTML info about the classes
    tables = browser.find_elements(By.XPATH, '//table[contains(@cellpadding, "3")]')
    
    
    end_time = time.localtime()
    diff = (time.mktime(end_time) - time.mktime(start_time)) 
    if(diff >= sleepTime and len(tables) == 0):     # Check for timeout issues
        print(time.strftime("%H:%M:%S",end_time), " -Timeout error occured")


        for c in classParent.winfo_children():
            c.destroy()
        Label(classParent, text = "Timeout Error Occuered...", font = ("helvetica", 20), name = "error_msg").pack()
        Label(classParent, text = "Please ensure you have a stable internet connection and try again.", font = ("helvetica", 10)).pack()
        
        return None


    elif len(tables) == 0:          # Return nothing if no results were found TODO Change this for the current program
        return None
        
    else:   # Parse and display the gathered data
        print(time.strftime("%H:%M:%S",end_time), "    -Results found (", str(len(tables)) , ")")
    
        loadData.clear()

        try:
            # Old slower way
            # for x in range(0, len(tables)):

            #     entry = tables[x].text.split('\n')
            #     # Corner case for first class
            #     if('Arts, Sciences, and Engineering Computer Science' in entry):
            #         entry.remove('Arts, Sciences, and Engineering Computer Science')

            #     loadData.append(make_course(entry))

            # # Print the finishing time
            # print(time.strftime("%H:%M:%S", time.localtime()), "    -Results parsed")

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

                try:
                    dict["Title"] = str(table.xpath(".//span[contains(@id,'lblCNum')]/text()")[0]) + " " + str(table.xpath(".//span[contains(@id,'lblTitle')]/text()")[0])
                except:
                    pass
                
                try:
                    dict["Days"] =  str(table.xpath(".//span[contains(@id,'lblDay')]/text()")[0])
                except:
                    pass

                try:
                    dict["Term"] =  str(table.xpath(".//span[contains(@id,'lblTerm')]/text()")[0])
                    
                except:
                    pass

                try:
                    dict["Credit"] = str(table.xpath(".//span[contains(@id,'lblCredits')]/text()")[0])   
                    
                except:
                    pass

                try:
                    dict["Open"] = "Open" == str(table.xpath(".//span[contains(@id,'lblStatus')]/text()")[0])
                except:
                    pass

                try:
                    dict["Start"] = int(table.xpath(".//span[contains(@id,'lblStartTime')]/text()")[0])
                except:
                    pass

                try:
                    dict["End"] =  int(table.xpath(".//span[contains(@id,'lblEndTime')]/text()")[0])
                except:
                    pass

                try:
                    dict["Room"] =  str(table.xpath(".//span[contains(@id,'lblBuilding')]/text()")[0])
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
                    dict["Instructor"] =  str(table.xpath(".//span[contains(@id,'lblInstructors')]/text()")[0])
                except:
                    pass

                try:    #TODO separate restrictions from this section

                    for children in table.xpath(".//span[contains(@id,'lblDesc')]"):
                     for x in children.itertext():
                         dict["Description"] += x + "\n"
                except:
                    pass

                try:
                    dict["Offered"] = table.xpath(".//span[contains(@id,'lblOffered')]/text()")[0].split(" ")

                    if "" in dict["Offered"]:
                        dict["Offered"].remove("")
                except:
                    pass

                loadData.append(dict)

        except Exception as e: 
            print("Error reading / parsing data")
            print(e)


            
            
        browser.implicitly_wait(sleepTime)



def save_and_quit():
    print("Closing...")
    out = open("saved_classes.json", "w")
    json_out_data = json.dumps(current_classes)
    out.write(json_out_data)
    out.close()

    # browser.close()
    root.destroy()

#============================================ Set up the Tkinter window ============================================#
# Set up the root window for the app
bgColor = '#121212'

customtkinter.set_default_color_theme("green")
root = customtkinter.CTk()
# root.protocol("WM_DELETE_WINDOW", on_closing)
root.title('CDCS Visualizer')  #Title for window
root.geometry("890x580")
root.option_add("*Font", ("Adobe Garamond Pro Bold", 10))
root.protocol("WM_DELETE_WINDOW", save_and_quit)

#===================== Calender Component =====================#

calander_frame = customtkinter.CTkFrame(root)
plan= customtkinter.CTkCanvas(calander_frame, width = 440, height = 580)

plan.pack( pady = 0)


num_credits_label = 0
num_classes_label = 0

canvas_num_courses = customtkinter.CTkLabel(calander_frame, text = "Number of Classes Chosen: " + str(num_classes_label))

canvas_num_credits = customtkinter.CTkLabel(calander_frame, text = "Number of Credits Chosen: " + str(num_credits_label))


# canvas_num_courses.pack()
canvas_num_credits.pack()
draw_cal()


calander_frame.pack(side=RIGHT, anchor = "n")
#===================== Search Component =====================#
tabview = customtkinter.CTkTabview(root,  height = 600, width = 400)
tabview.add("Find Classes")
tabview.add("Search Results")
tabview.add("Current Classes")

searchPane = customtkinter.CTkFrame(tabview.tab("Find Classes"), width = 200, height = 100)


styleT = ttk.Style()
styleT.configure('TCombobox', selectbackground=None, selectforeground=None)

searchLeft = customtkinter.CTkFrame(searchPane, fg_color="transparent")
searchRight = customtkinter.CTkFrame(searchPane, fg_color="transparent")



browser.get('https://cdcs.ur.rochester.edu/')

xmlSrc = lxml.html.fromstring(browser.page_source)



yearTitle = customtkinter.CTkLabel(searchLeft, text="Term (REQUIRED)").pack(anchor='w')
yearSelect = customtkinter.CTkComboBox(searchLeft, state="readonly", values = (xmlSrc.xpath('//*[@id="ddlTerm"]/option/text()')))

yearSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
yearSelect.pack()



subjectTitle = customtkinter.CTkLabel(searchLeft, text="Subject:").pack(anchor='w')
subjectSelect = customtkinter.CTkComboBox(searchLeft,state="readonly", values = (xmlSrc.xpath('//*[@id="ddlDept"]/option/text()')))     # 
# subjectSelect.bind('<KeyRelease>', manage_combobox)
subjectSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
subjectSelect.pack()




typeTitle = customtkinter.CTkLabel(searchLeft, text="Course Type:").pack(anchor='w')
typeSelect = customtkinter.CTkComboBox(searchLeft, state="readonly", values = (xmlSrc.xpath('//*[@id="ddlTypes"]/option/text()')))

typeSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
typeSelect.pack()



courseTitle = customtkinter.CTkLabel(searchRight, text="Course ID:").pack(anchor='w')
courseSelect = customtkinter.CTkEntry(searchRight)
courseSelect.pack()


titleTitle = customtkinter.CTkLabel(searchRight, text="Course Keywords:").pack(anchor='w')
titleSelect = customtkinter.CTkEntry(searchRight)
titleSelect.pack(pady = (0, 11), anchor='n')

search_btn = customtkinter.CTkButton(searchRight, text = "SUBMIT", command=lambda :fetch(yearSelect.get(), subjectSelect.get(), typeSelect.get())).pack()


searchLeft.pack(side= LEFT, padx=(22,6), pady = 4)
searchRight.pack(side= RIGHT, padx=(6,22))
searchPane.pack(anchor="nw", padx =10)


showResults = False







#===================== Results Component =====================#



classParent = customtkinter.CTkScrollableFrame(tabview.tab("Search Results"), height = 450,  width = 400)
classParent.pack()




scroll_next = customtkinter.CTkButton(tabview.tab("Search Results"), text="Next", command=next_page, anchor="se",).pack(side = RIGHT)
scroll_prev = customtkinter.CTkButton(tabview.tab("Search Results"), text="Prev", command=prev_page, anchor="sw").pack(side = LEFT)

scroll_text = customtkinter.CTkLabel(tabview.tab("Search Results"), text="Showing " + str(indxS) + "-" + str(indxE) + " of " + str(numResults),font=customtkinter.CTkFont(size=10, weight="bold"))
scroll_text.pack(side = BOTTOM)

tabview.pack(anchor = 'nw', padx = 10)


selectedParent = customtkinter.CTkScrollableFrame(tabview.tab("Current Classes"), height = 500, width = 400)
selectedParent.pack()

# Load all of the current saved clsses into the scroll pane
for entry in range(0,len(current_classes)):
        added_class_pane(current_classes[entry]) 



# customtkinter.set_appearance_mode("Light")

root.mainloop()

