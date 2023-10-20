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



loadData = []  # json.loads(open("scraped_classes.json", "r").read())
load_dropbox = json.loads(open("dropbox_info.json", "r").read())

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


def make_text(parent, dict):
    text = Text(parent,  font="Helvetica 9", spacing1=5, wrap=WORD, height = 12, width=55, bd = 0)
    text.tag_configure("r", font="Helvetica 9")
    text.tag_configure("bold", font="Helvetica 9 bold")
    text.tag_configure("blue",foreground="blue")
    text.tag_configure("red",foreground="red")

    text.insert("end", dict["Title"] + "\n","blue") 
    text.insert("end", "                                                " + dict["Term"] + "\n", "bold" ) 
    text.insert("end", "Days: ","bold", str("".join(dict["Days"])), "r","   Start: ", "bold", str(dict["Start"]), "r", "  End: ","bold", (str(dict["End"])), "r",  "                Credit: " + dict["Credit"] + "\n", 'red')
    text.insert("end", "Enrolled: ","bold", dict["Enrolled"] + '/' + dict["Capacity"] + "\n") 
    text.insert("end", "Instructor: ","bold", dict["Instructor"] + "\n") 
    text.insert("end", "Room: ","bold", dict["Room"] + "\n") 
    text.insert("end", "Description: ","bold", dict["Description"] + "\n") 
    text.insert("end", "Offered: ","bold", " ".join(dict["Offered"])) 

    # print(int(text.count("1.0", "end", "displaylines")[0] / 50.0))
    # print(int(text.index('end-1c').split('.')[0]))
    text.configure(state="disabled")
    text.pack()
    

def create_class_pane(dict):
    global classParent
    f=Frame(classParent,  relief= GROOVE, bd=3, bg = "white")
    make_text(f,dict)
    btn = Button(f, text="Add to Schedule", height = 1, command=lambda *args: add_course(dict)).pack(side = BOTTOM, anchor="se", padx = 4, pady = 4)
    f.pack(pady = 5)
    # classParent.configure(height = classParent.winfo_height() + 100)
    # classParent.update_idletasks()

#FIXME find out how to use tags to easily locate panes for different courses
def added_class_pane(dict):
    global classParent
    f=Frame(classParent,  relief= GROOVE, bd=3, bg = "white", name = dict["Title"].lower())
    make_text(f,dict)
    Button(f, text="Remove from Schedule", height = 1, command=lambda *args: remove_course(dict, f)).pack(side = RIGHT, anchor="se", padx = 4, pady = 4)

    var = tkinter.IntVar()
    var.set(int(not dict["Showing"]))
    Checkbutton(f, text = "Hide Class", anchor = "w", variable=var, command=lambda *args: toggle_show(dict, var), relief=RIDGE, bd = 2).pack( side =LEFT,  anchor="sw", padx = 4, pady = 4)    
    f.pack(pady = 5)

    toggle_show(dict, var)
    # classParent.configure(height = classParent.winfo_height() + 100)
    # classParent.update_idletasks()

def toggle_show(course, var):   #Intermediate function to work with IntVar so courses can be serialized using json
    #FIXME add color changes to pane here (and maybe add_class_pane) so they update when classes are changed
    if var.get() == 0:
        course["Showing"] = True
    else:
        course["Showing"] = False
        change_wiget_color("#c7cdd6", classParent.nametowidget(course["Title"].lower()))
        
    update_overlap()
    draw_cal()

def update_overlap():       #FIXME update so that this also controls the colors of the classes on the clander from draw_cal() method?
    for course in current_classes:
        if course["Showing"]:
            try:
                change_wiget_color("white", classParent.nametowidget(course["Title"].lower()))
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
                            change_wiget_color("#ffc2cc", classParent.nametowidget(other["Title"].lower()))
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


    canvas_num_courses["text"] = "Number of Classes Chosen: " + str(num_classes_label)


    if int(num_credits_label) >= 20:
        canvas_num_credits["text"] = "Number of Credits Chosen: " + str(num_credits_label) + " (OVERLOAD)"
        canvas_num_credits["fg"] = "red"
    else:
        canvas_num_credits["text"] = "Number of Credits Chosen: " + str(num_credits_label)
        canvas_num_credits["fg"] = "black"
    
    


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

    plan.create_rectangle(x,y,x + 80,y + lengthOff, fill = color)
    plan.create_text(x + 2, y, anchor="nw", text = title, fill  = 'white',font=("helvetica",8) )
    plan.create_text(x + 4, y + 15, anchor="nw", text = timeStr, fill  = 'white',font=("helvetica",7))



# Functions for changing display on pages
def change_displayed_courses(startI, endI):
    global classParent
    # classParent.configure(height = 0)
    scroll.set(0.0, scroll.get()[1] - scroll.get()[0])
    classParent.destroy()
    classParent = Frame(canvas)

    for entry in range(startI-1,endI):
        create_class_pane(loadData[entry])              

    canvas.create_window(0, 0, anchor='nw', window=classParent)
    canvas.update_idletasks()

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
        if results_swap_btn["text"] ==  "Show Availible Courses":
            swap_panes()
        reset_page()


def fetch(term, dept ="", type = "", courseName = ""):

    if results_swap_btn["text"] ==  "Show Availible Courses":
            swap_panes()


    for c in classParent.winfo_children():
        c.destroy()

    textx = Label(classParent, text = "Searching for results...", font = ("helvetica", 20)).pack()

    courseName = courseSelect.get("1.0",END)
    desc = titleSelect.get("1.0",END)

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

# # Turn the HTML data into a dictionary for each course #FIXME outdated helper function from above
# def make_course(data):

#     dict = {"Title": "",
#             "Days": "",
#             "Term": "",
#             "Credit": "",
#             "Open": False,
#             "Start": "",
#             "End": "",
#             "Room": "",
#             "Capacity": "",
#             "Enrolled": "",
#             "Instructor": "",
#             "Description": "",
#             "Restrictions": [],
#             "Offered": "",
#             "Showing": True}
    
#     tmp = data[1].split(" ")
#     dict["Term"] = tmp[-4] + " " +  tmp[-3]
#     dict["Credit"] = tmp[-2]
#     dict["Open"] = tmp[-1] == "Open"

#     if tmp[-6] == "-":
#         dict["Credit"] = tmp[-5]
#         for i in range(0,len(tmp) - 6):
#             dict["Title"] = dict["Title"] + " " +tmp[i]
#     else: 
#         for i in range(0,len(tmp) - 4):
#             dict["Title"] = dict["Title"] + " " +tmp[i]


#     for item in data:
#         if ("Day Begin End Location Start Date End Date") in item:
#             if  not ("Enrollment") in data[data.index(item) + 1]:
#                 items = data[data.index(item) + 1].split(" ")
#                 dict["Days"] = list(items[0])
#                 dict["Start"] = int(items[1])
#                 dict["End"] = int(items[2])

#                 for r in items[3:-2]:
#                     dict["Room"] = dict["Room"] + " " + r
                    
#         if ("Capacity") in item:
#             dict["Enrolled"] = item[0:item.index(" ")]
#             dict["Capacity"] = data[data.index(item) + 1]

#         if ("Instructors") in item:
#             dict["Instructor"] = item[12:]

#         if ("Description") in item:
#             dict["Description"] = item[12:]

#         if ("Offered") in item:
#             dict["Offered"] = item[9:].split(" ")
#     return dict

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
root = Tk()
# root.protocol("WM_DELETE_WINDOW", on_closing)
root.title('CDCS Visualizer')  #Title for window
root.geometry("890x650")
root.option_add("*Font", ("Adobe Garamond Pro Bold", 10))
root.protocol("WM_DELETE_WINDOW", save_and_quit)

#===================== Calender Component =====================#

calander_frame = Frame(root)
plan= Canvas(calander_frame, width = 440, height = 580, bd=0,highlightthickness=2,  relief='ridge')

plan.pack( anchor = 'nw', pady = 0)


num_credits_label = 0
num_classes_label = 0

canvas_num_courses = Label(calander_frame, text = "Number of Classes Chosen: " + str(num_classes_label))

canvas_num_credits = Label(calander_frame, text = "Number of Credits Chosen: " + str(num_credits_label))


canvas_num_courses.pack()
canvas_num_credits.pack()
draw_cal()

calander_frame.pack(side=RIGHT, anchor = "n")
#===================== Search Component =====================#


searchPane = Frame(root, width = 200, height = 100, relief=GROOVE, bd = 2)


styleT = ttk.Style()
styleT.configure('TCombobox', selectbackground=None, selectforeground=None)

searchLeft = Frame(searchPane)
searchRight = Frame(searchPane)



yearTitle = Label(searchLeft, text="Term (REQUIRED)", fg = "red").pack(anchor='w')
yearSelect = ttk.Combobox(searchLeft,width = 32, state="readonly", values = load_dropbox["Term"])

yearSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
yearSelect.pack()


# def manage_combobox(event):
#     value = event.widget.get()

#     if value == '':
#         subjectSelect['values'] = load_dropbox["Dept"]

#     else:
#         data = []
#         for item in load_dropbox["Dept"]:
#             if value.lower() in item.lower():
#                 data.append(item)
#         data.sort()
#         subjectSelect['values'] = data

subjectTitle = Label(searchLeft, text="Subject:").pack(anchor='w')
subjectSelect = ttk.Combobox(searchLeft, width = 32,state="readonly", values = load_dropbox["Dept"])     # 
# subjectSelect.bind('<KeyRelease>', manage_combobox)
subjectSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
subjectSelect.pack()






typeTitle = Label(searchLeft, text="Course Type:").pack(anchor='w')
typeSelect = ttk.Combobox(searchLeft,width = 32, state="readonly", values = load_dropbox["Type"])

typeSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
typeSelect.pack()

courseTitle = Label(searchRight, text="Course ID:").pack(anchor='w')
courseSelect = Text(searchRight, height = 1, width = 15, relief=SOLID, bd = 1)
courseSelect.pack()


titleTitle = Label(searchRight, text="Course Keywords:").pack(anchor='w')
titleSelect = Text(searchRight, height = 1, width = 15, relief=SOLID, bd = 1)
titleSelect.pack(pady = (0, 11), anchor='n')

search_btn = Button(searchRight, text = "SUBMIT", command=lambda :fetch(yearSelect.get(), subjectSelect.get(), typeSelect.get())).pack()


searchLeft.pack(side= LEFT, padx=(22,6), pady = 4)
searchRight.pack(side= RIGHT, padx=(6,22))
searchPane.pack(anchor="nw", padx =10)


showResults = False
def swap_panes():
    global classParent, showResults, results_swap_btn

    scroll.set(0.0, scroll.get()[1] - scroll.get()[0])
    classParent.destroy()
    classParent = Frame(canvas)


    if showResults:
        for entry in range(indxS-1,indxE):
            create_class_pane(loadData[entry])  
        showResults = FALSE
        results_swap_btn["text"] = "Show Chosen Courses" 
    else:
        for entry in range(0,len(current_classes)):
            added_class_pane(current_classes[entry])   
        showResults = True           
        results_swap_btn["text"] =  "Show Availible Courses"

    canvas.create_window(0, 0, anchor='nw', window=classParent)
    canvas.update_idletasks()






#===================== Results Component =====================#

scrolingPane = Frame(root,  relief= GROOVE, bd=3, height = 800)
scroll_title = Label(scrolingPane, text="Results", font=("Helvetica 8 bold")).pack(anchor = "nw")

results_swap_btn = Button(scrolingPane, text = "Show Chosen Courses", command=swap_panes)
results_swap_btn.pack(anchor = "ne", side = TOP)


canvas = Canvas(scrolingPane,width=390, height = 420)
scroll = Scrollbar(scrolingPane, orient="vertical", command=canvas.yview)

classParent = Frame(canvas, height = 14700)

# for entry in range(0,50):
#     create_class_pane(loadData[entry])

classParent.pack_forget()

canvas.create_window(0, 0, anchor='nw', window=classParent)
canvas.update_idletasks()
canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll.set)
    
scroll.pack(fill='y', side='left', anchor='w')
canvas.pack(fill='both', expand=True, side='top')

scroll_next = Button(scrolingPane, text="Next", command=next_page, anchor="se",).pack(side = RIGHT)
scroll_prev = Button(scrolingPane, text="Prev", command=prev_page, anchor="sw").pack(side = LEFT)

scroll_text = Label(scrolingPane, text="Showing " + str(indxS) + "-" + str(indxE) + " of " + str(numResults), font=("Helvetica 6 bold"))
scroll_text.pack(side = BOTTOM)


scrolingPane.pack(anchor = 'nw', padx = 10)






root.mainloop()



# TODO: Remove below code? This was an old method for manually entering course information
# def submit_form():
#     global checkbox_list

#     className = course.get(1.0, END)
#     classTime = start_time.get(1.0, END)
#     for i in range(0,5):
#         if checkbox_list[i].get():
#             add_class(days[i], className, int(classTime), color = "red")


# f2=Frame(root, width=10, relief= SUNKEN, bd=1)

# submit = Button(f2, text="SUBMIT", command=submit_form)
# submit.pack(side = BOTTOM)

# Label(f2, text="Course Title").pack(side=TOP)
# course = Text(f2, height = 1, width = 15)
# course.pack()

# Label(f2, text="Start Time").pack(side=TOP)
# start_time = Text(f2, height = 1, width = 15)
# start_time.pack()
# m= tkinter.IntVar()
# t=  tkinter.IntVar()
# w =  tkinter.IntVar()
# r =  tkinter.IntVar()
# f=  tkinter.IntVar()
# Label(f2, text="M     T     W    R     F  ").pack(side=TOP, padx = 0)
# # for our frame we make and then pack 3 nice buttons with values
# mB = Checkbutton(f2, anchor=W, variable=m)

# tB = Checkbutton(f2, anchor=W, variable=t)

# wB = Checkbutton(f2, anchor=W, variable=w)

# rB = Checkbutton(f2, anchor=W, variable=r)

# fB = Checkbutton(f2, anchor=W, variable=f)
# fB.pack(anchor=W, side=RIGHT)
# rB.pack(anchor=W, side=RIGHT)
# wB.pack(anchor=W, side=RIGHT)
# tB.pack(anchor=W, side=RIGHT)
# mB.pack(anchor=W, side=RIGHT)
# checkbox_list = [m,t,w,r,f]

# f2.pack(side = LEFT, padx= 20)
