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
from pathlib import Path

#TODO: fix minor errors,  restrictions scraping (addig bold to this text), 
#  dropdown menues for selected courses, add graphical elements when searching for quereys / no results are found, make
# sure that any classes that are added are for the same semester


# Error with using dict["Title"] as a widget name when the title contains a special character

#Error with hide unavailable classses missing a few classes that still show up as red and CLOSED later on

# Add a check that if someone signs up for a workshop, they also sign up for the lecture (dropdown menu for workshop classes from main lecture class?)


# Known errors: FUNCTION REDUNDANCY, errors with connecting to CDCS & exiting connection on program close, 
#  scroll pane doesn't work unless over the bar (scrolling on the
# individual frames instead), setting scroll bar location after a search, finding what hight the course panes should 
# be according to the wrapped text, errors with UI element placing and consistancy, error when scraping credits that 
# "Wrokshop" isn't recognized or set up correctly in the scraper




# TODO for overlapping classes, add a yellow triangle in the bottom right with the number of classes in that space
# For writing classes, workshops, recitations, add something to make it stand out on the calender
day_lookup = {"M":"Monday", "T":"Tuesday", "W":"Wednesday", "R":"Thursday", "F":"Friday", "S":"Saturday", "U":"Sunday"}


color1 = "#fcfc5d"
bg1 = "#f5f5bf"
color2 = "#5ec1ff"
bg2 = "#c5e6fa"

# Create something that merges the looks of the dropdown course menues with scrolable frames that act like comboboxes
class CustomDropDown(Frame):
    def __init__(self, parent,text,img, width,text_width, values,list_width=38, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)
        self.text = text
        self.values = values

        # Create canvas and entry box
        self.canvas = Canvas(self, width = width, height = 60, bg= "#7268A6", bd=0,highlightthickness=0)
        self.canvas.create_image(2,2, anchor = "nw", image= img)
        self.entry = Entry(self,bg="#B29EC6",fg= "#f2f4f1",font=("IstokWeb Bold", 20 * -1),bd=0, width = text_width)
        self.entry.place(in_=self.canvas, x=5, y = 27, anchor="w")
        self.entry.insert(0, self.text)

        
        # Create frame and scroll bar for options
        self.scroll_frame = Frame(self)
        self.scroll_frame.pack_forget()
        scrollbar = Scrollbar(self.scroll_frame)
        scrollbar.pack( side = RIGHT, fill=Y )

        self.list = Listbox(self.scroll_frame,width = list_width, yscrollcommand = scrollbar.set, borderwidth=0, highlightthickness=0,selectmode=SINGLE)  
        self.list.pack( side = LEFT,anchor="s", fill = BOTH )
    
        scrollbar.config(command = self.list.yview)
        self.canvas.pack(anchor="n",side=TOP)


        # Bind events
        self.entry.bind('<Button-1>', self.clear_text)

        if self.values != None:
            self.entry.bind('<KeyRelease>', self.manage_input)
            self.list.bind('<Button-1>', self.select_option)


    def clear_text(self, event):
        # Used to clear the starting text in th entry and toggle the drop down list
        if self.entry.get() == self.text:
            self.entry.delete(0,len(self.text)+ 1)

            for i in range(len(self.values)):
                self.list.insert(self.list.size(), self.values[i])

        if self.values != None:
            self.scroll_frame.pack(side=BOTTOM)


    def manage_input(self, event):
        # Used to change what is shown in hte drop down list
        self.list.config(height= 11)
        value = self.entry.get()
        self.list.delete(0, self.list.size())

        if value == '':
            for i in range(len(self.values)):
                self.list.insert(self.list.size(), self.values[i])
            

        else:   #TODO try to condense following lines
            data = []
            for item in self.values:
                if value.lower() in item.lower():
                    data.append(item)
            data.sort()
            for i in range(len(data)):
                self.list.insert(self.list.size(), data[i])
            

        if len(data) < 11:
            self.list.config(height= len(data))
            


    def select_option(self, event): #FIXME Error with different widgets getting input from each other??
        # Used to select a value from the drop down list
        try:    #FIXME edge case when first selescting a value
            if self.entry.get() != self.list.selection_get():
                self.entry.delete(0,len(self.entry.get()))
                self.entry.insert(0, self.list.selection_get())
                self.list.selection_clear(0, len(self.values))
                self.scroll_frame.forget()
        except:
            pass
       
    def get(self):
        # Get the current entry text

        if self.entry.get() == self.text:
            return "" #Make sure starting text isn't passed forward
        return self.entry.get()



class CustomCombobox(ttk.Combobox):
    def __init__(self, parent,values = None, startingText = '',fg = 'black',  *args, **kw):
        ttk.Combobox.__init__(self, parent, *args, **kw)
        self.values = values
        self['values'] = values

        self.startingText = startingText
        self.set(startingText)
        self.configure(foreground="#777777")

        self.fg = fg

        self.bind('<Button-1>', self.manage_initial_text)
        self.bind('<KeyRelease>', self.manage_combobox)

    def manage_initial_text(self, event):

        if self.get() == self.startingText:
            self.set('')
            self.configure(foreground=self.fg)


    def manage_combobox(self, event):
        value = event.widget.get()

        if value == '':
            self['values'] = self.values

        else:
            data = []
            for item in self.values:
                if value.lower() in item.lower():
                    data.append(item)
            data.sort()
            self['values'] = data

    def reset(self):
        self.set(self.startingText)
        self.configure(foreground="#777777")
        self['values'] = self.values






def update_overlap():       #TODO update so that this also controls the colors of the classes on the clander from draw_cal() method?
    for course in current_classes:
        if course["Showing"]:
            try:
                cur_courses_pane.interior.nametowidget(course["Title"].lower())._change_mode("normal")
            except:
                pass

    for course in current_classes:
        if course["Showing"]:
            
            for day in course["Days"]:
                for other in current_classes:
                    if not other == course and day in other["Days"] and other["Showing"] and ((other["Start"] <= course["Start"] and course["Start"] <= other["End"]) or (course["Start"] <= other["Start"] and other["Start"] <= course["End"])):
                        try:
                            cur_courses_pane.interior.nametowidget(course["Title"].lower())._change_mode("overlap")
                            cur_courses_pane.interior.nametowidget(other["Title"].lower())._change_mode("overlap")
                        except:
                            pass
                
        


class ModernCourseElement(ttk.Frame):
    def __init__(self, parent,dict = None, type = "g",mode=TRUE , *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

       
        self.dict = dict
        self.type = type
        self.mode = mode


        if self.type == "b":
            self.add_img = btn_b_add
            self.info_img = btn_b_info
            self.banner_img = banner_b
            self.body_img = body_b
            self.bg_color = "#ADD8E5"
        elif self.type == "o":
            self.add_img = btn_o_add
            self.info_img = btn_o_info
            self.banner_img = banner_o
            self.body_img = body_o
            self.bg_color = "#FFF684"
        else: #TYPE == "G"
            self.add_img = btn_g_add
            self.info_img = btn_g_info
            self.banner_img = banner_g
            self.body_img = body_g
            self.bg_color = "#D8D8D8"

        self.show_img = btn_show_img
        self.hide_img = btn_hide_img
        self.remove_img = btn_remove_b

        self.canvas = Canvas(self, bg = "#FFFFFF",height = 54,width = 680,bd = 0,highlightthickness = 0,relief = "ridge")
        self.canvas.create_rectangle(0,0,681.0,54,fill="#EDEDED",outline="")
        self.draw_banner()

                
        self.btn_info = Button(self.canvas,image=self.info_img, borderwidth=0,highlightthickness=0,command = lambda *args: self.toggle_dropdown(),relief="flat")
        self.btn_info.place(in_=self.canvas,x=579.0,y=7.0,width=95.0,height=21.0)#width and height are 2 less than they should be: hack to fix white border on click #FIXME

        if mode:  #Mode represents if its a search element or a result element
            self.btn_add = Button(self.canvas,image=self.add_img,borderwidth=0,highlightthickness=0,command = lambda: self.add_course_to_schedule(),relief="flat")
            self.btn_add.place(in_=self.canvas,x=507.0,y=7.0,width=52.0,height=21.0) #width and height are 2 less than they should be: hack to fix white border on click #FIXME
        else:   #TODO make these rely on local values, not the global ones
            self.btn_remove = Button(self.canvas,image=self.remove_img,borderwidth=0,highlightthickness=0,command = lambda: self.remove_course_from_schedule(),relief="flat")
            self.btn_remove.place(in_=self.canvas,x=507.0,y=7.0,width=62.0,height=21.0) #width and height are 2 less than they should be: hack to fix white border on click #FIXME

            self.btn_show = Button(self.canvas,image=self.hide_img,borderwidth=0,highlightthickness=0,command = lambda: self.toggle_show(),relief="flat")
            self.btn_show.place(in_=self.canvas,x=600.0,
                y=34.0,
                width=52.0,
                height=14.0) #width and height are 2 less than they should be: hack to fix white border on click #FIXME


        self.canvas.pack(pady = (10,0))
        self.pack(anchor="w")

    def toggle_dropdown(self):
        if self.canvas.winfo_height() <= 60:
            self.make_text(self.dict)
        else:
            self.canvas.config(height=54)
            self.canvas.create_rectangle(0,0,681.0,54,fill="#EDEDED",outline="")
            self.draw_banner()
           
        
    def draw_banner(self):
        # Create banner
        self.canvas.create_image(0,0, anchor=NW, image=self.banner_img)

        # Course Number
        self.canvas.create_text(14.0,9.0,anchor="nw",text=self.dict["Title"],fill="#FFFFFF",font=("IstokWeb Bold", 16 * -1, "bold"))

        days = []
        for d in self.dict["Days"]:
            days.append(day_lookup[d])

        self.canvas.create_text(100.0,30.0,anchor="nw",text=("/".join(days) + ": " + time_to_str(self.dict["Start"]) + " - " + time_to_str(self.dict["End"])),fill="#FFFFFF",font=("IstokWeb Bold", 12 * -1, "bold"))

        self.canvas.create_text(20.0,30.0,anchor="nw",text=self.dict["Credit"] + " credits",fill="#FFFFFF",font=("IstokWeb Bold", 12 * -1, "bold"))

        if self.dict["Open"]:
            self.canvas.create_text(454.0,9.0,anchor="nw",text="Open",fill="#FFFFFF",font=("IstokWeb Bold", 14 * -1, "bold"))
        else:
            self.canvas.create_text(454.0,9.0,anchor="nw",text="Closed",fill="#FFFFFF",font=("IstokWeb Bold", 14 * -1, "bold"))
        #Split this into 2 that sit on top of each other?
        # canvas.create_text(170.0,9.0,anchor="nw",text="Monday/Wednesday: 615pm - 730 pm",fill="#FFFFFF",font=("IstokWeb Bold", 14 * -1))


    def make_text(self, dict):     
        #Find number of lines needing and manually wrap text
        t = self.dict["Description"].split(" ")
        the_text = "                       " # Buffer hack for spaing on bold description
        line = ""
        for i in range(len(t)):
            if t[i][:1] == "\n":
                line += "\n"
                the_text += line
                line = t[i]

            elif len(line) + len(t[i]) + 1 <= 110:
                line += " " + t[i]
            else:
                line += "\n"
                the_text += line
                line = t[i]
        the_text += line


        #This is the number of lines the text will be
        num_lines = the_text.count("\n")

        # Dynamically size canvas and bg to the text length
        self.canvas.config(height=140 + 12 * max(0,num_lines-3) + 72)
        self.canvas.create_rectangle(0,0,681.0,140 + 12 * max(0,num_lines-3) + 72,fill="#EDEDED",outline="")
        self.canvas.create_image(0,140 + 12 * max(0,num_lines-3), anchor=NW, image=self.body_img)
        self.canvas.create_rectangle(0.0,20.0,681.0,140 + 12 * max(0,num_lines-3),fill=self.bg_color,outline="")

        self.draw_banner()

        # Title & Enrolled
        self.canvas.create_text(7.0,66.0,anchor="nw",text=self.dict["Title"],fill="#000000",font=("IstokWeb", 14 * -1, "bold"))
        self.canvas.create_text(573.0,66.0,anchor="nw",text= dict["Enrolled"] + "/" + dict["Capacity"] +" Enrolled",fill="#000000",font=("IstokWeb Bold", 12 * -1, "bold"))
        
        # Semesters offered
        self.canvas.create_text(7.0,89.0,anchor="nw",text="Offered: ",fill="#000000",font=("IstokWeb Bold", 12 * -1,'bold'))
        self.canvas.create_text(57.0,89.0,anchor="nw",text=(", ".join(self.dict["Offered"])),fill="#000000",font=("IstokWeb Bold", 12 * -1))

        # Instructor           
        self.canvas.create_text(7.0,106.0,anchor="nw",text="Instructor: ",fill="#000000",font=("IstokWeb Bold", 12 * -1, "bold"))
        self.canvas.create_text(70.0,106.0,anchor="nw",text=self.dict["Instructor"],fill="#000000",font=("IstokWeb Bold", 12 * -1))

        # Room
        self.canvas.create_text(7.0,123.0,anchor="nw",text="Room: ",fill="#000000",font=("IstokWeb Bold", 12 * -1,'bold'))
        self.canvas.create_text(47.0,123.0,anchor="nw",text=self.dict["Room"],fill="#000000",font=("IstokWeb Bold", 12 * -1))

        # Class description
        self.canvas.create_text(7.0,140.0,anchor="nw",text="Description: ",fill="#000000",font=("IstokWeb Bold", 12 * -1,'bold'))
        self.canvas.create_text(7.0,140.0,anchor="nw",text=the_text,fill="#000000",font=("IstokWeb Bold", 12 * -1))


    def toggle_show(self):
        #FIXME info button not switching colors, error
        if self.dict["Showing"]:
            # Switch button images
            self.btn_show.config(image=self.show_img)
            self.btn_info.config(image=btn_g_info)
            self.btn_remove.config(image=btn_remove_g)
            self.dict["Showing"] = False

            #Set color type to g
            self.banner_img = banner_g
            self.body_img = body_g
            self.bg_color = "#D8D8D8"


        else:
            # Switch button images
            self.btn_show.config(image=self.hide_img)
            self.btn_info.config(image=self.info_img)
            self.btn_remove.config(image=self.remove_img)
            self.dict["Showing"] = True

            # Set pallet back to normal
            if self.type == "b":
                self.banner_img = banner_b
                self.body_img = body_b
                self.bg_color = "#ADD8E5"
            elif self.type == "o":
                self.banner_img = banner_o
                self.body_img = body_o
                self.bg_color = "#FFF684"
            else: # Safety case (type == "g")
                self.banner_img = banner_g
                self.body_img = body_g
                self.bg_color = "#D8D8D8"

        self.draw_banner()
        #TODO make a check if the body needs to be redrawn
        update_overlap()
        draw_cal()
        draw_header()


    def add_course_to_schedule(self):
        if self.dict not in current_classes:
            current_classes.append(self.dict)

            if(len(current_classes) % 2 == 1):
                ModernCourseElement(cur_courses_pane.interior,self.dict,mode=FALSE, type ="b")
            else:
                ModernCourseElement(cur_courses_pane.interior,self.dict,mode=FALSE, type ="b")
            for day in self.dict["Days"]:
                draw_class( day, " ".join(self.dict["Title"].split(" ")[0:3]), self.dict["Start"], color = "blue")
        update_overlap()
        draw_cal()
        draw_header()


    def remove_course_from_schedule(self):
        if(self.dict in current_classes):
            current_classes.remove(self.dict)
            
        self.destroy()
        draw_cal()
        draw_header()


        


class VerticalScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
 
        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0, 
                                width = 400, height = 550,
                                yscrollcommand=vscrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command = self.canvas.yview)
 
        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
 
        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = ttk.Frame(self.canvas)
        self.interior.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=NW)
 
 
    def _configure_interior(self, event):
        # Update the scrollbars to match the size of the inner frame.
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion=(0, 0, size[0], size[1]))
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the canvas's width to fit the inner frame.
            self.canvas.config(width = self.interior.winfo_reqwidth())
         
    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the inner frame's width to fill the canvas.
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def _clear_contents(self):
        for c in self.interior.winfo_children():
            c.destroy()



theme = ["#E85A4F", "#E98074", "#8E8D8A", "#D8C3A5", "#EAE7DC"]

loadData = []  # json.loads(open("scraped_classes.json", "r").read())
load_dropbox = json.loads(open("dropbox_info.json", "r").read())

current_classes = json.loads(open("saved_classes.json", "r").read())

days = ["M", "T", "W","R","F"]
days2 = ["Monday", "Tuesday", "Wednesday","Thursday","Friday"]

# Indexes for shown results
indxS= 1
indxE = 0
numResults = len(loadData)

sleepTime = 20  #For timeout checks


# Print initial time
print(time.strftime("%H:%M:%S", time.localtime()), "    -Searching for webpage")


# Set up browser connection     FIXME
options = Options()
options.add_argument("--headless")
browser = webdriver.Firefox(options=options)
browser.implicitly_wait(sleepTime)


def time_to_str(time):
    if type(time) is int:
        ret = time
        if ret > 1300:
            ret -= 1200
        
        ret = str(ret)
        

        ret = ret[:-2] + ":" + ret[-2:]

        if time >= 1200:
            ret += "pm"
        else:
            ret += "am"
        return ret
    return ""




def draw_header():
    global header

    header.create_rectangle(0,0,430,70,width = 0, fill = theme[0])
    header.create_text(10,10, text = current_classes[0]["Offered"], anchor = "nw", fill = "white")

    num_courses = 0
    for course in current_classes:
        if course["Showing"]:
            num_courses += 1

    create_rounded_square(header, 200, 10 , 20, 20, "white", r=5)
    header.create_text(210,20, text = str(num_courses), anchor = "center", fill = theme[0])
    header.create_text(225,20, text = "courses", anchor = "w", fill = "white")
    
    num_credits = int(get_num_credits())
    create_rounded_square(header, 280, 10 , 20, 20, "white", r=5)
    header.create_text(290,20, text = str(num_credits), anchor = "center", fill = theme[0])

    if num_credits >= 20:
        header.create_text(305,20, text = "credits (OVERLOAD)", anchor = "w", fill = "white")
    else:
        header.create_text(305,20, text = "credits", anchor = "w", fill = "white")

   

def get_num_credits():
    num_credits = 0

    for course in current_classes:
        if course["Showing"]:
            try:
                num_credits += float(course["Credit"])
            except:
                pass
    return num_credits




#TODO fix so elements get deleted with tags instead of having to redraw the entire canvas
def draw_cal(): #  Draw the background for the calender
    global classParent
    plan.delete('all')

    plan.create_line(0,0,14 +  400,0)
    for i in range(0,5):
        x = 25 +  i * 80
        # plan.create_line(x,20,x,580)
        plan.create_text(x + 40,10, text=days2[i],  anchor = "center")

    hours = ["", "8", "9","10","11", "12", "1", "2", "3","4","5", "6", "7","8", ""]
    for i in range(1,14):
        x = 10 +  i * 40
        plan.create_line(25,x,415,x, fill = theme[1])
        plan.create_text(20,x, text= hours[i], anchor = "e", fill=  theme[1])


    for course in current_classes:
        if course["Showing"]:
            
            overlap = False
            for day in course["Days"]:
                for other in current_classes:
                    if not other == course and day in other["Days"] and other["Showing"] and ((other["Start"] <= course["Start"] and course["Start"] <= other["End"]) or (course["Start"] <= other["Start"] and other["Start"] <= course["End"])):
                        overlap = True

            for day in course["Days"]:
                if overlap:
                    draw_class(day, " ".join(course["Title"].split(" ")[0:2]), course["Start"], color = "red")
                else:
                    draw_class(day, " ".join(course["Title"].split(" ")[0:2]), course["Start"], color = "blue")

    
    



def draw_class(day = "", title = "", timeStart = 0, length = 115, color = "blue"):   #Add a block to the calender
    time = timeStart - 700
    rem = time % 100
    y = (time // 100) * 40 + ((rem / 60) * 40) + 10
    x = 25 +  days.index(day) * 80
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


    create_rounded_square(plan, x + 2,y, 76 , lengthOff, color)


    plan.create_text(x + 4, y + 2, anchor="nw", text = title, fill  = 'white',font=("helvetica",10) )
    plan.create_text(x + 4, y + 15, anchor="nw", text = timeStr, fill  = 'white',font=("helvetica",8))


#TODO / FIXME update to aa circle
def create_rounded_square(canvas, x, y, width, height, color, r = 10):
    canvas.create_rectangle(x + r,y,x +width - r ,y + height, fill = color,width = 0)   # vertical
    canvas.create_rectangle(x ,y + r ,x + width,y + height - r, fill = color, width = 0) #horizontal

    canvas.create_aa_circle(x + r, y + r, r , fill = color)  # top left
    canvas.create_aa_circle(x + width - r, y + r, r, fill = color) # top right
    canvas.create_aa_circle(x + r, y + height - r, r, fill = color) # bot left
    canvas.create_aa_circle(x + width - r,  y + height - r, r, fill = color) # bot right


# Functions for changing display on pages  
def change_displayed_courses(startI, endI):
    global result_courses_pane
    # result_courses_pane._clear_contents()
    # for c in result_courses_pane.interior.winfo_children():
    #     c.destroy()
    result_courses_pane.destroy()                               #FIXME quick hack for functionality
    result_courses_pane = VerticalScrolledFrame(results)
    result_courses_pane.pack()


    for entry in range(startI-1,endI):
        if entry % 2 ==0:
            ModernCourseElement(result_courses_pane.interior,loadData[entry], type = "b")
            
        else:
            ModernCourseElement(result_courses_pane.interior,loadData[entry], type = "b")
     


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

        if hide_unavailable_var.get() == 1:
            print("Removing unavailable classes...")

            for dict in loadData:
                if not dict["Open"] or dict["Enrolled"] >= dict["Capacity"]:
                    loadData.remove(dict)

        reset_page()
        


def fetch(term, dept ="", type = "", courseName = ""):
    global result_courses_pane, unavailable_classes_check
    tabview.select(results)

    
    

    # result_courses_pane._clear_contents()
    # for c in result_courses_pane.interior.winfo_children():
    #         c.destroy()

    result_courses_pane.destroy()                               #FIXME quick hack for functionality
    result_courses_pane = VerticalScrolledFrame(results)
    result_courses_pane.pack()


    courseName = id_box.get()
    desc = keywords_box.get()

    # Make sure starting text isn't passed to the program
    # if dept == subject_box.text:
    #         dept = ""

    # if type == course_box.text:
    #     type = ""

    print(term, dept, type, courseName, desc)

    # Verify that the combobox values are valid
    if term in semester_box.values and dept in subject_box.values and type in course_box.values:
        thread = threading.Thread(target=scrapeHTML, args=[term, dept, type,courseName,desc])
        thread.start()
        root.after(200, check_if_ready, thread)

    else:   #TODO make this message better
        tkinter.messagebox.showerror(title="Search Box Error", message="INVALID SEARCH (make sure selected values are valid options)")
        print("INVALID SEARCH (make sure selected values are valid options)")
    




def scrapeHTML(term, dept ="", type = "", courseName = "", desc = ""):
    global loadData
    print("Finding courses...")

     #TODO make an actual element for searching
    text_tmp = Label(result_courses_pane.interior, text = "Searching for results...", font = ("helvetica", 20)).pack()

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
        tkinter.messagebox.showerror(title="Search TImeout Error", message="Timeout Error Occured. Please make sure you are connected to a stable internet connection, or increase the timeout duration.")
        #TODO add a graphical element if a timeout connection occured
        return None


    elif len(tables) == 0:          # Return nothing if no results were found TODO Change this for the current program
        return None
        
    else:   # Parse and display the gathered data
        print(time.strftime("%H:%M:%S",end_time), "    -Results found (", str(len(tables)) , ")")
    
        loadData.clear()

        try:
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
        return 0



def save_and_quit():
    global browser
    print("Closing...")
    out = open("saved_classes.json", "w")
    json_out_data = json.dumps(current_classes)
    out.write(json_out_data)
    out.close()
    browser.close()

    root.destroy()

#============================================ Set up the Tkinter window ============================================#
# Set up the root window for the app
print(time.strftime("%H:%M:%S", time.localtime()), "    -Creating GUI")

root = Tk()
root.title('UR Ready')  #Title for window
root.geometry("1200x600")
root.option_add("*Font", ("Adobe Garamond Pro Bold", 10))
# root.configure(background=theme[0])

root.protocol("WM_DELETE_WINDOW", save_and_quit)

#===================== Load Assets =====================#

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


btn_o_info = PhotoImage(
    file=relative_to_assets("info_o.png"))
btn_o_add = PhotoImage(
    file=relative_to_assets("add_o.png"))
banner_o = PhotoImage(
    file=relative_to_assets("banner_o.png"))
body_o = PhotoImage(
    file=relative_to_assets("body_o.png"))

btn_b_info = PhotoImage(
    file=relative_to_assets("info_b.png"))
btn_b_add = PhotoImage(
    file=relative_to_assets("add_b.png"))
banner_b = PhotoImage(
    file=relative_to_assets("banner_b.png"))
body_b = PhotoImage(
    file=relative_to_assets("body_b.png"))

btn_g_info = PhotoImage(
    file=relative_to_assets("info_g.png"))
btn_g_add = PhotoImage(
    file=relative_to_assets("add_g.png"))
banner_g = PhotoImage(
    file=relative_to_assets("banner_g.png"))
body_g = PhotoImage(
    file=relative_to_assets("body_g.png"))

btn_show_img = PhotoImage(
    file=relative_to_assets("show_g.png"))
btn_hide_img = PhotoImage(
    file=relative_to_assets("hide_b.png"))
btn_remove_b = PhotoImage(
    file=relative_to_assets("remove_b.png"))
btn_remove_g = PhotoImage(
    file=relative_to_assets("remove_g.png"))


search_img  = PhotoImage(
    file=relative_to_assets("search_s.png"))
results_img  = PhotoImage(
    file=relative_to_assets("results.png"))
schedule_img  = PhotoImage(
    file=relative_to_assets("schedule.png"))
requirements_img  = PhotoImage(
    file=relative_to_assets("requirements.png"))

#Photo images for search widget
bg_img = PhotoImage(file=relative_to_assets("search_bg.png"))
search_btn_img = PhotoImage(file=relative_to_assets("search_btn.png"))
search_long_img = PhotoImage(file=relative_to_assets("search_long.png"))
search_short_img = PhotoImage(file=relative_to_assets("search_small.png"))

#===================== Calender Component =====================#

calander_frame = Frame(root, bd = 2, relief="solid")

header= customtkinter.CTkCanvas(calander_frame, width = 420, height = 35)
header.pack(pady=(0,0))

plan= customtkinter.CTkCanvas(calander_frame, width = 420, height = 580)
plan.pack( anchor = 'nw', pady=(0,0))


calander_frame.pack(side=RIGHT, anchor = "n", pady = 10, padx = 10)

draw_cal()
draw_header()

#===================== Set Up Tabview =====================#
tabposition = ttk.Style()
tabposition.configure('TNotebook', sticky='w', tabposition='nw',borderwidth=0,  highlightthickness = 0)
tabposition.layout("Tab",
[('Notebook.tab', {'sticky': 'nswe', 'children':
    [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
            [('Notebook.label', {'side': 'top', 'sticky': ''})],})],})])

tabview = ttk.Notebook(root,  height = 600, width = 400)
search = ttk.Frame(tabview)
results = ttk.Frame(tabview)
classes = ttk.Frame(tabview)
requirements = ttk.Frame(tabview)

tabview.add(search, image=search_img)
tabview.add(results, image = results_img)
tabview.add(classes, image=schedule_img)
tabview.add(requirements, image = requirements_img)

tabview.pack(expand = 1, fill ="both")




#===================== Search Component =====================#

print(time.strftime("%H:%M:%S", time.localtime()), "    -Getting Combobox Values")
browser.get('https://cdcs.ur.rochester.edu/')
xmlSrc = lxml.html.fromstring(browser.page_source)


searchPane = Frame(search, width = 200, height = 100, relief=GROOVE, bd = 2)


search_canvas = Canvas(searchPane,bg = "#F2F4F1",height = 400,width = 696,bd = 0,highlightthickness = 0,relief = "ridge")
search_canvas.create_image(102,59, anchor = "nw", image= bg_img)




# 1st long bar
# canvas.create_image(123,85, anchor = "nw", image= search_long_img)

semester_box = CustomDropDown(searchPane,text = "Semester (REQUIRED):", values = (xmlSrc.xpath('//*[@id="ddlTerm"]/option/text()')), width = 286, img = search_long_img, text_width = 25)
semester_box.place(in_=search_canvas, x=123,y=85)
try:
    semester_box.values.remove("SELECT A TERM")
except:
    print("SELECT A TERM text no longer on webpage")

# 2nd long bar
# canvas.create_image(123,161, anchor = "nw", image= search_long_img)
vals = (xmlSrc.xpath('//*[@id="ddlDept"]/option/text()'))
vals.insert(0,"")

subject_box = CustomDropDown(searchPane,text = "Subject:", values = vals, width = 286, img = search_long_img, text_width = 25)
subject_box.place(in_=search_canvas, x=123,y=161)

# 3rd long bar
# canvas.create_image(123,237, anchor = "nw", image= search_long_img)
vals =  (xmlSrc.xpath('//*[@id="ddlTypes"]/option/text()'))
vals.insert(0,"")

course_box = CustomDropDown(searchPane,text = "Course Type:", values = vals, width = 286, img = search_long_img, text_width = 25)
course_box.place(in_=search_canvas, x=123,y=237)




# 1st short bar
# canvas.create_image(429,85, anchor = "nw", image= search_short_img)
id_box = CustomDropDown(searchPane,text = "Course ID:", values = None, width = 146, img = search_short_img, text_width = 12, list_width=21)
id_box.place(in_=search_canvas, x=429,y=85)

# 2nd short bar
# search_canvas.create_image(429,161, anchor = "nw", image= search_short_img)
keywords_box = CustomDropDown(searchPane,text = "Keywords:", values = None, width = 146, img = search_short_img, text_width = 12, list_width=21)
keywords_box.place(in_=search_canvas, x=429,y=161)

# Checkbutton for hiding unavailable classes

hide_unavailable_var = tkinter.IntVar()
check_btn = Checkbutton(searchPane,bd=0,highlightthickness=0, background="#7268A6", activebackground="#7268A6",variable= hide_unavailable_var)
check_btn.place(in_=search_canvas, x = 361,y =310)
search_canvas.create_text(386.0,311.0,anchor="nw",text="Hide unavailable classes",fill="#FFFFFF",font=("IstokWeb Bold", 16 * -1))




#Keep lift order so widgets don't obscure each other
semester_box.lift(aboveThis=subject_box)
semester_box.lift(aboveThis=course_box)
subject_box.lift(aboveThis=course_box)
semester_box.lift(aboveThis=check_btn)
subject_box.lift(aboveThis=check_btn)
course_box.lift(aboveThis=check_btn)
id_box.lift(aboveThis=keywords_box)





search_canvas.pack()


# Search button for submitting form
search_btn = Button(image=search_btn_img,borderwidth=0,highlightthickness=0,command=lambda :fetch(semester_box.get(), subject_box.get(), course_box.get()),relief="flat")
search_btn.place(in_=search_canvas, x=447.0,y=234.0,width=103.0,height=60.0)





# styleT = ttk.Style()
# styleT.configure('TCombobox', selectbackground=None, selectforeground=None)

# searchLeft = Frame(searchPane)
# searchRight = Frame(searchPane)

# print(time.strftime("%H:%M:%S", time.localtime()), "    -Getting Combobox Values")
# browser.get('https://cdcs.ur.rochester.edu/')
# xmlSrc = lxml.html.fromstring(browser.page_source)


# # Create widgets for the search form
# yearTitle = Label(searchLeft, text="Term (REQUIRED)", fg = "red").pack(anchor='w')
# yearSelect = CustomCombobox(searchLeft,width = 32,values = (xmlSrc.xpath('//*[@id="ddlTerm"]/option/text()')),startingText="Semester (REQ) :")


# yearSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
# yearSelect.pack()

# subjectTitle = Label(searchLeft, text="Subject:").pack(anchor='w')
# vals = (xmlSrc.xpath('//*[@id="ddlDept"]/option/text()'))
# vals.insert(0,"")
# subjectSelect = CustomCombobox(searchLeft, width = 32,values =vals,startingText="Subject :")     # 
# subjectSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
# subjectSelect.pack()

# typeTitle = Label(searchLeft, text="Course Type:").pack(anchor='w')
# vals =  (xmlSrc.xpath('//*[@id="ddlTypes"]/option/text()'))
# vals.insert(0,"")
# typeSelect = CustomCombobox(searchLeft,width = 32,  values = vals,startingText="Type :")
# typeSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
# typeSelect.pack()

# hide_unavailable_var = tkinter.IntVar()
# unavailable_classes_check = Checkbutton(searchLeft, variable= hide_unavailable_var,  text = "Hide Unavailable Classes")
# unavailable_classes_check.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
# unavailable_classes_check.pack()



# courseTitle = Label(searchRight, text="Course ID:").pack(anchor='w')
# courseSelect = Text(searchRight, height = 1, width = 15, relief=SOLID, bd = 1)
# courseSelect.pack()

# titleTitle = Label(searchRight, text="Course Keywords:").pack(anchor='w')
# titleSelect = Text(searchRight, height = 1, width = 15, relief=SOLID, bd = 1)
# titleSelect.pack(pady = (0, 11), anchor='n')

# search_btn = Button(searchRight, text = "SUBMIT", command=lambda :fetch(yearSelect.get(), subjectSelect.get(), typeSelect.get())).pack()



# searchLeft.pack(side= LEFT, padx=(22,6), pady = 4)
# searchRight.pack(side= RIGHT, padx=(6,22))
searchPane.pack(anchor="nw", padx =10)



#===================== Results Component =====================#



scrolingPane = Frame(results, bd=0, width = 400)

scroll_next = Button(scrolingPane, text="Next", command=next_page, anchor="ne",).pack(side = RIGHT)
scroll_prev = Button(scrolingPane, text="Prev", command=prev_page, anchor="nw").pack(side = LEFT)

scroll_text = Label(scrolingPane, text="Showing " + str(indxS) + "-" + str(indxE) + " of " + str(numResults), font=("Helvetica 10 bold"))
scroll_text.pack(side = TOP, padx = 100)

scrolingPane.pack()

result_courses_pane = VerticalScrolledFrame(results)
result_courses_pane.pack()



#===================== Current Courses Component =====================#

cur_courses_pane = VerticalScrolledFrame(classes)
cur_courses_pane.pack()

# Load all of the current saved clsses into the scroll pane
for entry in range(0,len(current_classes)):
    if current_classes[entry]["Showing"]:
        ModernCourseElement(cur_courses_pane.interior,current_classes[entry],mode=FALSE, type ="b")
    else:
        print("not showing") #FIXME make sure classes that start as hidden are added as hidden
        ModernCourseElement(cur_courses_pane.interior,current_classes[entry],mode=FALSE, type = "b")



print(time.strftime("%H:%M:%S", time.localtime()), "    -Starting Program")
root.mainloop()



