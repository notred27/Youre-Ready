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
import logging



logger = logging.getLogger('UR_READY')
logger.setLevel(logging.DEBUG)

# fh = logging.StreamHandler()
fh = logging.FileHandler('ur_ready.log')
fh_formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)



#TODO when selecting a term, check if a json file for that semester already exists, and if so load it. If it doesn't create a new json file and load it.
#

#TODO: fix minor errors,  restrictions scraping (addig bold to this text), 
#   no results are found, 


# TODO make sure that any classes that are added are for the same semester

#Error with hide unavailable classses missing a few classes that still show up as red and CLOSED later on

# Add a check that if someone signs up for a workshop, they also sign up for the lecture (dropdown menu for workshop classes from main lecture class?)


# Known errors: FUNCTION REDUNDANCY, errors with connecting to CDCS & exiting connection on program close, 
#  scroll pane doesn't work unless over the bar (scrolling on the
# individual frames instead), setting scroll bar location after a search,  error when scraping credits that 
# "Wrokshop" isn't recognized or set up correctly in the scraper

#FIXME Error with hide on dropdown menu not changing bg color untill it is hidden again


# TODO for overlapping classes, add a yellow triangle in the bottom right with the number of classes in that space
# For writing classes, workshops, recitations, add something to make it stand out on the calender?

# FIXME when scraping classes, remove "" for offered (when course isnt offered during a semester)







day_lookup = {"U":"Sunday", "M":"Monday", "T":"Tuesday", "W":"Wednesday", "R":"Thursday", "F":"Friday", "S":"Saturday"}



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




class ModernCourseElement(Frame):
    def __init__(self, parent,dict = None, type = "g",mode=TRUE , *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

       
        self.dict = dict
        self.type = type
        self.mode = mode

        self.check_list = []
        
        self.cur_color = type

        self.num_sections = 0

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

        self.canvas = Canvas(self, bg = "#FFECDC",height = 54,width = 685,bd = 0,highlightthickness = 0,relief = "ridge")
        self.configure(background = "#FFECDC")
        self.canvas.create_rectangle(0,0,681.0,54,fill="#EDEDED",outline="")
        self.draw_banner()

        self.section_list = Frame(self.canvas, bg = self.bg_color, pady=0, borderwidth=2,bd = 2)
                
        self.btn_info = Button(self.canvas,image=self.info_img, borderwidth=0,highlightthickness=0,command = lambda *args: self.toggle_dropdown(),relief="flat")
        self.btn_info.place(in_=self.canvas,x=579.0,y=7.0,width=95.0,height=21.0)#width and height are 2 less than they should be: hack to fix white border on click #FIXME

        if mode:  #Mode represents if its a search element or a result element
            self.btn_add = Button(self.canvas,image=self.add_img,borderwidth=0,highlightthickness=0,command = lambda: self.add_course_to_schedule(),relief="flat")
            self.btn_add.place(in_=self.canvas,x=507.0,y=7.0,width=52.0,height=21.0) #width and height are 2 less than they should be: hack to fix white border on click #FIXME
        else:   
            self.btn_remove = Button(self.canvas,image=self.remove_img,borderwidth=0,highlightthickness=0,command = lambda: self.remove_course_from_schedule(),relief="flat")
            self.btn_remove.place(in_=self.canvas,x=507.0,y=7.0,width=62.0,height=21.0) #width and height are 2 less than they should be: hack to fix white border on click #FIXME

            self.btn_show = Button(self.canvas,image=self.hide_img,borderwidth=0,highlightthickness=0,command = lambda: self.toggle_show(),relief="flat")
            self.btn_show.place(in_=self.canvas,x=600.0,
                y=34.0,
                width=52.0,
                height=14.0) #width and height are 2 less than they should be: hack to fix white border on click #FIXME


        self.canvas.pack(pady = (5,0), padx = 0)
        self.pack(anchor="w")

        try:
            for section in dict["Sections"]:
                self.add_section(section)


        except Exception as e:
            print(e)
            pass



    def toggle_dropdown(self):
        if self.canvas.winfo_height() <= 60:
            self.make_text()
        else:
            self.canvas.config(height=54)
            self.canvas.create_rectangle(0,0,681.0,54,fill="#EDEDED",outline="")
            self.draw_banner()
           
        
    def draw_banner(self):
        # Create banner
        self.canvas.create_image(0,0, anchor=NW, image=self.banner_img)

        # Course Number

        title = self.dict["Title"].split(" ")
        title[1] = title[1][:3]
        self.canvas.create_text(14.0,9.0,anchor="nw",text=title,fill="#FFFFFF",font=("IstokWeb Bold", 16 * -1, "bold"))

        self.canvas.create_text(20.0,30.0,anchor="nw",text=self.dict["Credit"] + " credits",fill="#FFFFFF",font=("IstokWeb Bold", 12 * -1, "bold"))

        #Split this into 2 that sit on top of each other?
        # canvas.create_text(170.0,9.0,anchor="nw",text="Monday/Wednesday: 615pm - 730 pm",fill="#FFFFFF",font=("IstokWeb Bold", 14 * -1))


    def add_section(self, sec):#FIXME so this just uses dict and not separate argumens
        color = "#ffffff"
        if self.num_sections % 2:
            color = "#dbdbdb"


        # ["Title"], "", section["Instructor"], section["Days"], section["Time"], section["Room"], section["Enrolled"], section["Cap"], section["Showing"]
        section_frame = Canvas(self.section_list, width = 670, height = 24, bg=color, bd=0, highlightthickness=0)

        #FIXME maybe make frames for each line, but that would drastically increase the complexity
        # print(f'{title:<14}    {course_type:<14}    {instructor:<20}    {days:<20}    {time:<12}    {room:<12}')
        # l = Label(section_frame, text = f'{title:<14}{course_type:<20}{instructor:<30}{days:<20}{str(time):<12}{room:<20}{enrolled:<20}', bg=color,font=("IstokWeb Bold", 12 * -1, "bold"))

        section_frame.create_text(5,5, text=sec["Title"], anchor="nw",font=("IstokWeb Bold", 10 * -1, "bold"))
        # section_frame.create_text(70,5, text=sec["Type"], anchor="nw",font=("IstokWeb Bold", 10 * -1, "bold"))
        section_frame.create_text(140,5, text=sec["Instructor"], anchor="nw",font=("IstokWeb Bold", 10 * -1, "bold"))
        section_frame.create_text(255,5, text=sec["Days"] + " : " + time_to_str(sec["Time"]) + "-" + time_to_str(sec["End"]), anchor="nw",font=("IstokWeb Bold", 10 * -1, "bold"))
        section_frame.create_text(420,5, text=sec["Room"], anchor="nw",font=("IstokWeb Bold", 10 * -1, "bold"))
        section_frame.create_text(550,5, text= str(sec["Enrolled"]) + "/" + str(sec["Cap"]) +" Enrolled", anchor="nw",font=("IstokWeb Bold", 10 * -1, "bold"))


        var = BooleanVar()
        var.set(sec["Showing"])

        

        i = self.num_sections   #FIXME quick hack to get locla var instead of using pointer reference in th ebelow functrion
        check = Checkbutton(section_frame, text = "",variable=var, command = lambda: self.testcheck(i,sec), bg=color, pady=0)
        self.check_list.append(var)

        check.place(in_=section_frame, x=640, y = 0)

        if sec["Showing"]:
            calender_component.add_to_cal(self, sec)



        self.num_sections+= 1
        section_frame.pack(anchor="nw")


    def testcheck(self, i,sec): #TODO (rename this) update this so it changes the calender too
        sec["Showing"] = self.check_list[i].get()

        if self.check_list[i].get():
            calender_component.add_to_cal(self, sec)

        else:
            calender_component.remove_from_cal(sec)



        #Redraw the canvas
        calender_component.draw()

        

        # print(self.dict["Sections"][i]["Title"] + str(self.check_list[i].get()))

    def make_text(self):     
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
        self.canvas.config(height=140 + 12 * max(0,num_lines-3) + 72 + 25 * self.num_sections)
        self.canvas.create_rectangle(0,0,681.0,140 + 12 * max(0,num_lines-3) + 72 + 25 * self.num_sections,fill="#EDEDED",outline="")
        self.canvas.create_image(0,140 + 12 * max(0,num_lines-3)  + 25 * self.num_sections, anchor=NW, image=self.body_img)
        self.canvas.create_rectangle(0.0,20.0,681.0,140 + 12 * max(0,num_lines-3)  + 25 * self.num_sections,fill=self.bg_color,outline="")

        self.draw_banner()

        # Title
        self.canvas.create_text(7.0,66.0,anchor="nw",text=self.dict["Title"],fill="#000000",font=("IstokWeb", 14 * -1, "bold"))

        
        # Semesters offered
        self.canvas.create_text(7.0,89.0,anchor="nw",text="Offered: ",fill="#000000",font=("IstokWeb Bold", 12 * -1,'bold'))
        self.canvas.create_text(57.0,89.0,anchor="nw",text=(", ".join(self.dict["Offered"])),fill="#000000",font=("IstokWeb Bold", 12 * -1))


        self.canvas.create_window(7.0,125.0, window=self.section_list, width = 670, anchor="nw")

        # Class description
        self.canvas.create_text(7.0,125.0 + 25 * self.num_sections,anchor="nw",text="Description: ",fill="#000000",font=("IstokWeb Bold", 12 * -1,'bold'))
        self.canvas.create_text(7.0,125.0 + 25 * self.num_sections,anchor="nw",text=the_text,fill="#000000",font=("IstokWeb Bold", 12 * -1))



    def toggle_show(self):
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
            
            self.banner_img = banner_b
            self.body_img = body_b
            self.bg_color = "#ADD8E5"
            

        self.draw_banner()
        #TODO make a check if the body needs to be redrawn

        # draw_cal()
        calender_component.draw()
        # draw_header()

    def toggle_overlap(self, overlapping):  #FIXME finish implementing this?
       
        if overlapping:
            self.banner_img = banner_o
            self.body_img = body_o
            self.bg_color = "#FFF684"
            # Switch button images
            self.btn_show.config(image=self.show_img)
            self.btn_info.config(image=btn_o_info)
            self.btn_remove.config(image=btn_remove_g)
            # self.dict["Showing"] = False

            #Set color type to g
            self.banner_img = banner_o
            self.body_img = body_o
            self.bg_color = "#FFF684"

        self.draw_banner()

        # else:
        #     # Switch button images
        #     self.btn_show.config(image=self.hide_img)
        #     self.btn_info.config(image=self.info_img)
        #     self.btn_remove.config(image=self.remove_img)
        #     self.dict["Showing"] = True

        #     # Set pallet back to normal
            
        #     self.banner_img = banner_b
        #     self.body_img = body_b
        #     self.bg_color = "#ADD8E5"
            
                
            

        # #FIXME do i still need to call these with the way its set up?
        # self.draw_banner()
        # #TODO make a check if the body needs to be redrawn
        # update_overlap()
        # # draw_cal()
        # calender_component.draw()
        # draw_header()



    def add_course_to_schedule(self):   #FIXME
        if self.dict not in current_classes:
            current_classes.append(self.dict)

            
            ModernCourseElement(cur_courses_pane.interior,self.dict,mode=FALSE, type ="b")
            


            for section in self.dict["Sections"]:
                if section["Showing"]:
                    for day in section["Days"]:
                        calender_component.draw_class( day, " ".join(section["Title"]), section["Time"], color = "blue")   #FIXME trying to merge with the checklist

        # draw_cal()
        calender_component.draw()
        # draw_header()


    def remove_course_from_schedule(self):
        if(self.dict in current_classes):
            current_classes.remove(self.dict)
            
        self.destroy()
        # draw_cal()
        calender_component.draw()
    



class VerticalScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

 
        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0, bg='#FFECDC',
                                width = 690, height = 450,
                                yscrollcommand=vscrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command = self.canvas.yview)
 
        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
 
        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = ttk.Frame(self.canvas, width = 680)
        self.interior.bind('<Configure>', self._configure_interior)   #FIXME
        # self.canvas.bind('<Configure>', self._configure_canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=NW)
 
 
    def _configure_interior(self, event):
        # Update the scrollbars to match the size of the inner frame.
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion=(0, 0, size[0], size[1]))
        # if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
        #     # Update the canvas's width to fit the inner frame.
        #     self.canvas.config(width = self.interior.winfo_reqwidth())
         
    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the inner frame's width to fill the canvas.
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())


    def _clear_contents(self):
        for c in self.interior.winfo_children():
            c.destroy()



theme = ["#6B3074", "#7268A6", "#8E8D8A", "#D8C3A5", "#EAE7DC"]

loadData = []  # json.loads(open("scraped_classes.json", "r").read())

current_classes = json.loads(open("saved_classes.json", "r").read())

days = ["U", "M", "T", "W","R","F", "S"]


# Indexes for shown results
indxS= 1
indxE = 0
numResults = len(loadData)

sleepTime = 20   #For timeout checks


# Print initial time
logger.info("Searching for webpage")

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




   




#FIXME this needs to be reimplemented





class CalenderElement(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        self.header= Canvas(self, width = 535, height = 35, background=theme[0])
        self.canvas= Canvas(self, width = 535, height = 580)

        self.showing_sections = []
        self.parent_list = []

        self.save_btn = Button(self.header, image=cal_save, bd = 0, highlightthickness=0)   #TODO make function to save png of button
        self.save_btn.place(in_=self.header, x = 497, y = 4, width = 33, height = 33)

        self.header.pack(pady=(0,0))
        self.canvas.pack(pady=(0,0))

    def add_to_cal(self,parent, section):
        self.showing_sections.append(section)
        self.parent_list.append(parent)

    def remove_from_cal(self, section):
        idx = self.showing_sections.index(section)
        self.showing_sections.pop(idx)
        self.parent_list.pop(idx)

    def draw(self):
        self.canvas.delete('all')

        for i, d in enumerate(day_lookup):
            x = 15 +  i * 75
            self.canvas.create_text(x + int(75 / 2),10, text=day_lookup[d],  anchor = "center")

        hours = ["", "8", "9","10","11", "12", "1", "2", "3","4","5", "6", "7","8", ""]
        for h in range(1,14):
            x = 10 +  h * 40
            self.canvas.create_line(20,x,530,x, fill = theme[1])
            self.canvas.create_text(15,x, text= hours[h], anchor = "e", fill=  theme[1])


        for i, sec in enumerate(self.showing_sections):
            if self.parent_list[i].dict["Showing"]:
                overlap = False
                for j, other in enumerate(self.showing_sections):
                    for day in sec["Days"]:
                        if not sec == other and day in other["Days"] and other["Showing"] and self.parent_list[j].dict["Showing"] and ((other["Time"] <= sec["Time"] and sec["Time"] <= other["End"]) or (sec["Time"] <= other["Time"] and other["Time"] <= sec["End"])):
                            overlap = True
                            #TODO use section here to update both of the parents to the yellow class
                
                # self.parent_list[i].toggle_overlap(overlap)   #FIXME make this faster

                if overlap:
                    for day in sec["Days"]:
                        self.draw_class(day, " ".join(sec["Title"].split(" ")[0:2]), sec["Time"], color = "red")
                    
                else:
                    for day in sec["Days"]:
                        self.draw_class(day, " ".join(sec["Title"].split(" ")[0:2]), sec["Time"], color = "blue")
        self.draw_header()


    def draw_header(self):
        self.header.delete("all")

        try:
            self.header.create_text(10,10, text = current_classes[0]["Term"], anchor = "nw", fill = "white", font=("IstokWeb", 20 * -1, "bold"))    #FIXME change this to use an actual semester and not hardcoded
        except:
            self.header.create_text(10,10, text = "No Semester Selected", anchor = "nw", fill = "white", font=("IstokWeb", 20 * -1, "bold"))    #FIXME change this to use an actual semester and not hardcoded



        # Courses text
        num_courses = 0
        for i, sec in enumerate(self.showing_sections):
            if sec["Showing"] and self.parent_list[i].dict["Showing"]:
                num_courses += 1
        
        self.header.create_image(297,19, image = cal_square, anchor = "center")
        self.header.create_text(298,19, text = str(num_courses), anchor = "center", fill = theme[0], font=("IstokWeb", 14 * -1, "bold"))
        self.header.create_text(318,20, text = "courses", anchor = "w", fill = "white", font=("IstokWeb", 14 * -1))
        

        # Credits text
        num_credits = int(self.get_num_credits())

        self.header.create_image(392,19, image = cal_square, anchor = "center")
        self.header.create_text(393,19, text = str(num_credits), anchor = "center", fill = theme[0],font=("IstokWeb", 14 * -1, "bold"))
        if num_credits >= 20:
            self.header.create_text(413,19, text = "credits (OL!)", anchor = "w", fill = "white", font=("IstokWeb", 14 * -1))
        else:
            self.header.create_text(413,19, text = "credits", anchor = "w", fill = "white", font=("IstokWeb", 14 * -1))


    def get_num_credits(self):  #FIXME change this to depend on the sections (although you will need to refer to the parent dict to get the credit value)
        num_credits = 0

        for course in current_classes:
            if course["Showing"]:
                try:
                    num_credits += float(course["Credit"])
                except:
                    pass
        return num_credits
    

    def draw_class(self, day = "", title = "", timeStart = 0, length = 115, color = "blue"):   #FIXME change length to depend on actual length of the class
        time = timeStart - 700  #700 is offset for canvas   #FIXME change this formatting for placing classes to be cleaner?
        rem = time % 100
        y = (time // 100) * 40 + ((rem / 60) * 40) + 10
        x = 17 +  days.index(day) * 75
        lengthOff = (length // 100) * 40 + ((length % 100 / 60) * 40)


        if color == "blue":
            self.canvas.create_image(x,y,image=cal_blue, anchor = "nw")
            self.canvas.create_image(x,y + lengthOff  - 15,image=cal_blue_bot, anchor = "nw")  

            self.canvas.create_rectangle(x ,y + 15 ,x + 72,y + lengthOff  - 15, fill = "#1597D5", width = 0) 
        else:
            self.canvas.create_image(x,y,image=cal_red, anchor = "nw")
            self.canvas.create_image(x,y + lengthOff  - 15,image=cal_red_bot, anchor = "nw") 

            self.canvas.create_rectangle(x ,y + 15 ,x + 72,y + lengthOff  - 15, fill = "#D51515", width = 0) 

        

        self.canvas.create_text(x + 5, y + 5, anchor="nw", text = title, fill  = 'white',font=("IstokWeb", 10 * -1, "bold") )
        self.canvas.create_text(x + 5, y + 20, anchor="nw", text = time_to_str(timeStart)[:-2] + "-" + time_to_str(timeStart + length)[:-2], fill  = 'white',font=("IstokWeb", 9 * -1))



        

        


        


# Functions for changing display on pages  
def change_displayed_courses(startI, endI):
    global result_courses_pane
    # result_courses_pane._clear_contents()
    # for c in result_courses_pane.interior.winfo_children():
    #     c.destroy()
    result_courses_pane.destroy()                               #FIXME quick hack for functionality
    result_courses_pane = VerticalScrolledFrame(results)
    notebook.add_element(result_courses_pane, "results", 10, 10, anchor="nw")


    for entry in range(startI-1,endI):
        
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





def check_if_ready(thread): #TODO use this thread to also update a loading image in the search canvas??
    # Function for threading the fetch request to backend website
    if thread.is_alive():
        # not ready yet, run the check again soon
        root.after(200, check_if_ready, thread)
    else:
        logger.info("Scraping Thread has terminated, updating page")

        if hide_unavailable_var.get() == 1:
            logger.info("Removing unavailable classes")

            
        reset_page()
        #somehow get the value of the thread here to set special flag images (i.e. no results/invalid search)   #TODO


        


def fetch(term, dept ="", type = "", courseName = ""):
    global result_courses_pane, unavailable_classes_check

    notebook.switch_tab(1)  #FIXME I was lazy so change this to be not hard coded to 1
    
    

    # result_courses_pane._clear_contents()
    # for c in result_courses_pane.interior.winfo_children():
    #         c.destroy()

    result_courses_pane.destroy()                               #FIXME quick hack for functionality
    result_courses_pane = VerticalScrolledFrame(results)
    notebook.add_element(result_courses_pane, "results", 10, 10, anchor="nw")


    courseName = id_box.get()
    desc = keywords_box.get()

    # Verify that the combobox values are valid, and start threaded search
    if term in semester_box.values and dept in subject_box.values and type in course_box.values:
        thread = threading.Thread(target=scrapeHTML, args=[term, dept, type,courseName,desc])
        thread.start()
        root.after(200, check_if_ready, thread)
        
    else:   
        #TODO fix bg color
        Label(result_courses_pane.interior, image = invalid_search_img, anchor="center").pack(side=TOP, padx = 180)

        tkinter.messagebox.showerror(title="Search Box Error", message="INVALID SEARCH (make sure selected values are valid options)")
        logger.error("INVALID SEARCH (make sure selected values are valid options)")
    




def scrapeHTML(term, dept ="", type = "", courseName = "", desc = ""):
    global loadData

     #TODO fix bg color
    Label(result_courses_pane.interior, image = searching_img, anchor="center").pack(side=TOP, padx = 140)



    logger.info("Search query: %s, %s, %s, %s, %s",term, dept, type, courseName, desc)

    # Connect to the page to clear past searches
    browser.get('https://cdcs.ur.rochester.edu/')
    logger.info("Connected to CDCS Webpage")

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
    logger.info("Form submitted to CDCS")
    
    # Recieve HTML info about the classes
    tables = browser.find_elements(By.XPATH, '//table[contains(@cellpadding, "3")]')
    
    
    end_time = time.localtime() #FIXME check to make sure this actually catches timeout errors
    diff = (time.mktime(end_time) - time.mktime(start_time)) 
    if(diff >= sleepTime and len(tables) == 0):     # Check for timeout issues
        logger.error("Timeout error occured")

        tkinter.messagebox.showerror(title="Search TImeout Error", message="Timeout Error Occured. Please make sure you are connected to a stable internet connection, or increase the timeout duration.")
        return None


    elif len(tables) == 0:          # Return nothing if no results were found TODO add graphical element
        logger.warning("No results found")
        return None
        
    else:   # Parse and display the gathered data
        logger.info("%d results found ", len(tables))
    
        loadData.clear()    # Discard previous search results

    
        browser.implicitly_wait(0.001)  #Change action time to be fast
        root = lxml.html.fromstring(browser.page_source)

        seen_classes = [] # Record which 'parent' courses we have seen so far

        for table in root.xpath('//table[contains(@cellpadding, "3")]'): #FIXME make this parsing better
            try: #Get the title for the class
                course_title = str(table.xpath(".//span[contains(@id,'lblCNum')]/text()")[0]).split(" ")
                course_title[1] = course_title[1][:3]
                course_title = " ".join(course_title)   #Formatting magic to get just the department and code



                if course_title in seen_classes:
                    # Find the overall course
                    parent = list(filter(lambda course: course_title in course['Title'] , loadData))[0]
                    # Add a new section to the  parent

                    create_section(table, parent["Sections"])
   
                    

                else:   # We haven't seen the parent course yet
                    seen_classes.append(course_title)

                    dict = {"Title": "",
                        "Term": "",
                        "Credit": "",
                        "Sections": [],

                        "Description": "",
                        "Restrictions": [],
                        "Offered": "",
                        "Showing": True}

                    try:
                        dict["Title"] = str(table.xpath(".//span[contains(@id,'lblCNum')]/text()")[0]) + " " + str(table.xpath(".//span[contains(@id,'lblTitle')]/text()")[0])
                        
                    except Exception as e:
                        print(e)
                        pass
                    

                    try:
                        dict["Term"] =  str(table.xpath(".//span[contains(@id,'lblTerm')]/text()")[0])
                        
                    except:
                        pass

                    try:
                        dict["Credit"] = str(table.xpath(".//span[contains(@id,'lblCredits')]/text()")[0])   
                        
                    except:
                        pass

                    try:    #TODO separate restrictions from this section(idk if I still need this as the text length currently captures restrictions)

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
                    
                    
                    
                       
                    create_section(table, dict["Sections"])
                    loadData.append(dict)


            except Exception as e: 
                logger.error("Error reading / parsing data")
                logger.error("%s", e)
            
        browser.implicitly_wait(sleepTime)
        return None    #TODO fix this return?
    




def create_section(table, parent):
    section = {"Title":"",
                "Type":"",
                "Instructor":"",
                "Days":"",
                "Time":0,
                "End":0,
                "Room":"",
                "Enrolled":"",
                "Cap":"",
                "Open":False,
                "Showing": False}


    try:
        section["Title"] = str(table.xpath(".//span[contains(@id,'lblCNum')]/text()")[0])
    except:
        pass

    #TODO add type
    
    try:
        section["Instructor"] =  str(table.xpath(".//span[contains(@id,'lblInstructors')]/text()")[0])
    except:
        pass

    try:    
        section["Days"] =  str(table.xpath(".//span[contains(@id,'lblDay')]/text()")[0])
    except:
        pass

    #FIXME add time conversion and day conversion here
    try:
        section["Time"] = int(table.xpath(".//span[contains(@id,'lblStartTime')]/text()")[0])
    except:
        pass

    try:
        section["End"] =  int(table.xpath(".//span[contains(@id,'lblEndTime')]/text()")[0])
    except:
        pass

    try:
        section["Room"] =  str(table.xpath(".//span[contains(@id,'lblBuilding')]/text()")[0])
    except:
        pass


    try:
        section["Cap"] =table.xpath(".//span[contains(@id,'lblSectionCap')]/text()")[0]
    except:
        pass

    try:
        section["Open"] = ("Open" == str(table.xpath(".//span[contains(@id,'lblStatus')]/text()")[0]))
    except:
        pass

    try:
        section["Enrolled"] =  table.xpath(".//span[contains(@id,'lblSectionEnroll')]/text()")[0]
    except:
        pass

    if not (not section["Open"] or section["Enrolled"] >= section["Cap"]):  #TODO do I want this behavior?
        parent.append(section)





def save_and_quit():
    global browser
    logger.info("Closing Program and saving chosen classes")
    try:
        out = open("saved_classes.json", "w")
        json_out_data = json.dumps(current_classes)
        out.write(json_out_data)
        out.close()
        
    except:
        logger.error("Unable to save classes")

    browser.close()
    root.destroy()

#============================================ Set up the Tkinter window ============================================#
# Set up the root window for the app
logger.info("Creating GUI")


root = Tk()


root.configure(background='white')

root.title('UR-Ready')  #Title for window
root.geometry("1280x650")
# root.option_add("*Font", ("Adobe Garamond Pro Bold", 10))

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


search_up  = PhotoImage(
    file=relative_to_assets("search_up.png"))
res_up  = PhotoImage(
    file=relative_to_assets("res_up.png"))
sch_up = PhotoImage(
    file=relative_to_assets("sch_up.png"))
req_up  = PhotoImage(
    file=relative_to_assets("req_up.png"))
info_up  = PhotoImage(
    file=relative_to_assets("info_up.png"))

info_down  = PhotoImage(
    file=relative_to_assets("info_down.png"))
search_down  = PhotoImage(
    file=relative_to_assets("search_down.png"))
res_down  = PhotoImage(
    file=relative_to_assets("res_down.png"))
sch_down = PhotoImage(
    file=relative_to_assets("sch_down.png"))
req_down  = PhotoImage(
    file=relative_to_assets("req_down.png"))

tab_body  = PhotoImage(
    file=relative_to_assets("folder_body.png"))

prev_btn_img  = PhotoImage(
    file=relative_to_assets("last_btn.png"))
next_btn_img  = PhotoImage(
    file=relative_to_assets("next_btn.png"))

searching_img  = PhotoImage(
    file=relative_to_assets("searching_img.png"))
invalid_search_img  = PhotoImage(
    file=relative_to_assets("invalid_search_img.png"))



cal_blue  = PhotoImage(
    file=relative_to_assets("cal_blue.png"))
cal_red  = PhotoImage(
    file=relative_to_assets("cal_red.png"))
cal_blue_bot  = PhotoImage(
    file=relative_to_assets("cal_blue_bot.png"))
cal_red_bot  = PhotoImage(
    file=relative_to_assets("cal_red_bot.png"))
cal_save  = PhotoImage(
    file=relative_to_assets("save.png"))
cal_square  = PhotoImage(
    file=relative_to_assets("rounded.png"))


#Photo images for search widget
bg_img = PhotoImage(file=relative_to_assets("search_bg.png"))
search_btn_img = PhotoImage(file=relative_to_assets("search_btn.png"))
search_long_img = PhotoImage(file=relative_to_assets("search_long.png"))
search_short_img = PhotoImage(file=relative_to_assets("search_small.png"))

#===================== Calender Component =====================#





calender_component = CalenderElement(root, bd = 2, relief="solid")

calender_component.pack(side=RIGHT, anchor = "n", pady = 10, padx = (2,2))

calender_component.draw()





#===================== Set Up Tabview =====================#

class CustomTabview(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)
        self.frame_list = []
        self.btn_list = []
        self.btn_img_list = []

        self.current_frame = None
        self.tab_frame = Frame(self, bd = 0, highlightthickness=0)
        self.content_frame = Frame(self, bd = 0, highlightthickness=0)
        self.configure(background='white')
        self.tab_frame.configure(background='white')
        self.content_frame.configure(background='white')  


        self.tab_frame.pack(side = TOP, anchor="nw", pady = 0)
        self.content_frame.pack_propagate(0)
        self.content_frame.pack(side=TOP, fill="both", expand = True,pady = 0)


    def switch_tab(self, i):
        for j, btn in enumerate(self.btn_list):
            if j == i:
                self.btn_list[j].config(image= self.btn_img_list[j][1])
            else:
                self.btn_list[j].config(image= self.btn_img_list[j][0])

        if not self.current_frame is self.frame_list[i]:
            self.current_frame.grid_forget()
            self.current_frame = self.frame_list[i]
            self.frame_list[i].grid(row=1,column=1)


    def add_tab(self, id, btn_imgs = None, **kwargs):
        frame = Canvas(self.content_frame, name=id,bg="white", bd = 0, highlightthickness=0,  **kwargs)
        frame.configure(background='white')  
        frame.create_image(0,0, image=tab_body, anchor="nw")
    
        i = len(self.frame_list)     # use  and index by tab
        tab = Button(self.tab_frame, text=id, borderwidth=0,bg='white', highlightthickness=0, command=lambda: self.switch_tab(i))
        tab.pack(side=LEFT, padx=(0,5))

        self.frame_list.append(frame)
        self.btn_list.append(tab)
        self.btn_img_list.append(btn_imgs)

        if btn_imgs != None:
            tab.config(image=btn_imgs[0])

        if len(self.frame_list) == 1:   
            self.current_frame = frame
            if btn_imgs != None:
                tab.config(image = btn_imgs[1])
            frame.grid(row=1,column=1)

    def add_element(self, elem, frame_name, x, y, anchor = "nw"):
        elem.place(in_= self.get(frame_name), x = x, y = y, anchor = "nw")


    def get(self, id):
        for f in self.frame_list:
            if f.winfo_name() == id:
                return f
        return None

        

notebook = CustomTabview(root, height = 600, width = 400)
notebook.add_tab("search", width = 1000,height = 1000, btn_imgs=(search_up,search_down))
notebook.add_tab("results",width = 1000,height = 1000, btn_imgs=(res_up, res_down))
notebook.add_tab("schedual",width = 1000,height = 1000,btn_imgs=(sch_up, sch_down))

notebook.add_tab("info",width = 1000,height = 1000,btn_imgs=(info_up, info_down))

# notebook.add_tab("requirements",width = 1000,height = 1000, btn_imgs=(req_up, req_down)) #TODO implement this?


notebook.pack(padx=5, pady=10)



#===================== Search Component =====================#

logger.info("Getting Combobox Values")

try:
    browser.get('https://cdcs.ur.rochester.edu/')
    xmlSrc = lxml.html.fromstring(browser.page_source)
except:
    logger.critical("Unable to load website resources")


search_canvas = notebook.get("search")


search_canvas.create_image(102,59, anchor = "nw", image= bg_img)


# 1st long bar
semester_box = CustomDropDown(search_canvas,text = "Semester (REQUIRED):", values = (xmlSrc.xpath('//*[@id="ddlTerm"]/option/text()')), width = 286, img = search_long_img, text_width = 25)
semester_box.place(in_=search_canvas, x=123,y=85)

try:
    semester_box.values.remove("SELECT A TERM")
except:
    logger.warning("SELECT A TERM text no longer on webpage")


# 2nd long bar
vals = (xmlSrc.xpath('//*[@id="ddlDept"]/option/text()'))
vals.insert(0,"")

subject_box = CustomDropDown(search_canvas,text = "Subject:", values = vals, width = 286, img = search_long_img, text_width = 25)
subject_box.place(in_=search_canvas, x=123,y=161)

# 3rd long bar
vals =  (xmlSrc.xpath('//*[@id="ddlTypes"]/option/text()'))
vals.insert(0,"")

course_box = CustomDropDown(search_canvas,text = "Course Type:", values = vals, width = 286, img = search_long_img, text_width = 25)
course_box.place(in_=search_canvas, x=123,y=237)

# 1st short bar
id_box = CustomDropDown(search_canvas,text = "Course ID:", values = None, width = 146, img = search_short_img, text_width = 12, list_width=21)
id_box.place(in_=search_canvas, x=429,y=85)

# 2nd short bar
keywords_box = CustomDropDown(search_canvas,text = "Keywords:", values = None, width = 146, img = search_short_img, text_width = 12, list_width=21)
keywords_box.place(in_=search_canvas, x=429,y=161)

# Checkbutton for hiding unavailable classes

hide_unavailable_var = tkinter.IntVar()
check_btn = Checkbutton(search_canvas,bd=0,highlightthickness=0, background="#7268A6", activebackground="#7268A6",variable= hide_unavailable_var)
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

# Search button for submitting form
search_btn = Button(search_canvas, image=search_btn_img,borderwidth=0,highlightthickness=0,command=lambda :fetch(semester_box.get(), subject_box.get(), course_box.get()),relief="flat")
search_btn.place(in_=search_canvas, x=447.0,y=234.0,width=103.0,height=60.0)



#===================== Results Component =====================#

results = notebook.get("results")

scroll_next = Button(results, image = next_btn_img, command=next_page, anchor="ne", bd = 0, highlightthickness=0)
notebook.add_element(scroll_next, "results", 645, 500)


scroll_prev = Button(results, image=prev_btn_img, command=prev_page, anchor="nw", bd = 0, highlightthickness=0)
notebook.add_element(scroll_prev, "results", 25, 500)

scroll_text = Label(results, text="Showing " + str(indxS) + "-" + str(indxE) + " of " + str(numResults), font=("IstokWeb", 14 * -1, "bold"), bg="#FFECDC")
notebook.add_element(scroll_text, "results", 335, 500, anchor="center")

result_courses_pane = VerticalScrolledFrame(results)
notebook.add_element(result_courses_pane, "results", 10, 10, anchor="nw")


#===================== Current Courses Component =====================#
classes = notebook.get("schedual")
cur_courses_pane = VerticalScrolledFrame(classes)
notebook.add_element(cur_courses_pane, "schedual", 10, 10, anchor="nw")

# Load all of the current saved clsses into the scroll pane
for entry in range(0,len(current_classes)):
    if current_classes[entry]["Showing"]:
        ModernCourseElement(cur_courses_pane.interior,current_classes[entry],mode=FALSE, type ="b")
    else:
        x = ModernCourseElement(cur_courses_pane.interior,current_classes[entry],mode=FALSE, type = "b")
        #FIXME make sure classes that start as hidden are added as hidden, quick hack but maybe make method to set for showing?

        x.toggle_show()
        x.toggle_show()

calender_component.draw()

#===================== Info Component =====================#
def change_timeout(new_time):
    global sleepTime

    try:
        sleepTime = int(new_time)
        logger.info("New timeout delay set")
    except:
        sleepTime = 20
    browser.implicitly_wait(sleepTime)
    
info = notebook.get("info")

info_dump = Text(info, width = 90, wrap=WORD,font=("IstokWeb", 12 * -1), bg="#FFECDC", bd=0, highlightthickness=0 )
      
info_dump.insert(END, "This application was created for recreational use, and is only intended to aid students in finding classes. ")
info_dump.insert(END, "It is in no way officially affiliated with the University of Rochester. ")
info_dump.insert(END, "All of the data used to populate the results for this application is publically available via the University of Rochester's UR Course Descriptions / Course Schedules (CDCS) website. ")
info_dump.insert(END, "All of the data in this application should be as up to date as possible, but any information on this application is not guaranteed to be accurate. ")

info_dump.insert(END, "If you find any bugs or errors, please reach out at (include email here) and include the application's .log file.")  #FIXME

info_dump.insert(END, "\n\n UR-Ready V3.0")
notebook.add_element(info_dump, "info", 10, 20, anchor="nw")





 
timeout_box = Entry(info, width=4)
timeout_box.insert(0,str(sleepTime))
timeout_box.bind('<KeyRelease>', (lambda event: change_timeout(timeout_box.get())))
notebook.add_element(timeout_box, "info", 10, 500, anchor="nw")
notebook.add_element(Label(info, text=" Timeout Delay (Seconds)", font=("IstokWeb", 14 * -1, "bold"), bg="#FFECDC"), "info", 35, 500, anchor="nw")

logger.info("Starting GUI Program")
root.mainloop()



