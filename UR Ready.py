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
#  dropdown menues for selected courses, add graphical elements when searching for quereys / no results are found

# Error with using dict["Title"] as a widget name when the title contains a special character

# Add a check that if someone signs up for a workshop, they also sign up for the lecture (dropdown menu for workshop classes from main lecture class?)


# Known errors: FUNCTION REDUNDANCY, errors with connecting to CDCS & exiting connection on program close, 
#  scroll pane doesn't work unless over the bar (scrolling on the
# individual frames instead), setting scroll bar location after a search, finding what hight the course panes should 
# be according to the wrapped text, errors with UI element placing and consistancy, hide PREV and NEXT buttons on 
# page for selected courses, error when scraping credits that "Wrokshop" isn't recognized or set up correctly in the scraper

# Update dynamic scroll bar resizing

# Bug with scroll bar not showing up



# TODO for overlapping classes, add a yellow triangle in the bottom right with the number of classes in that space
# For writing classes, workshops, recitations, add something to make it stand out on the calender


color1 = "#fcfc5d"
bg1 = "#f5f5bf"
color2 = "#5ec1ff"
bg2 = "#c5e6fa"

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


class AddedCourseElement(ttk.Frame):
    def __init__(self, parent,dict = None, color1 = "red", color2 = "green", *args, **kw):


        ttk.Frame.__init__(self, parent,name = dict["Title"].lower(), *args , **kw)

        self.color1 = color1
        self.color2 = color2
        self.dict = dict
        self.text = None

        self.cur_color = color2

        self.top_bar = Frame(self, bg = color1)
        self.label = Label(self.top_bar, bg = color1, font = customtkinter.CTkFont(size=15, weight="normal"), width = 65, anchor = "nw")


        lbl_txt =("%-*s %-*s" % (15, " ".join(dict["Title"].split(" ")[0:2]), 15, dict["Credit"]))
        if dict["Open"]:
            lbl_txt += ("%-*s : %-*.*s" %      (6,"Open", 20, 8, ("(" + dict["Enrolled"] + "/" + dict["Capacity"] + ")")))
        else:
            lbl_txt += ("%-*s : %-*.*s" %     ( 6,"Closed", 20,20, ("(" + dict["Enrolled"] + "/" + dict["Capacity"] + ")")))
        lbl_txt += ("%-*s : %s" % (3, dict["Days"], time_to_str(dict["Start"]) + " - " + time_to_str(dict["End"])))
        self.label["text"] = lbl_txt

        if not dict["Open"]:
            self.label["fg"] = "red"



        self.var = tkinter.IntVar()
        self.var.set(int(not dict["Showing"]))


        Checkbutton(self.top_bar, text = "Hide Class", variable=self.var, command= self.toggle_show, font = customtkinter.CTkFont(size=10, weight="normal"), relief=RIDGE, bd = 2).pack( side = RIGHT, anchor = "n", padx = 3,pady=2)   
        customtkinter.CTkButton(self.top_bar, text = "Remove",command=self.remove_course_from_schedule, fg_color="#ff8b05", width = 50, height = 20, font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", padx = 5, pady = 2)
        customtkinter.CTkButton(self.top_bar, text = "Info", command = self.toggle_dropdown, fg_color="#0000FF", width = 50, height = 20,  font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", pady = 2)
        

        self.label.pack()
        self.top_bar.pack(side = TOP, anchor="w")
        self.pack(anchor="w")

        self.toggle_show()

    def toggle_dropdown(self):
        if self.text == None:
            self.make_text()
        else:
            self.text.destroy()
            self.text = None

    def make_text(self):        
        self.text = Text(self,  padx = 5, font="Helvetica 9", spacing1=5, wrap=WORD, width=101, bd = 0, bg = self.cur_color)
        self.text.tag_configure("bold", font="Helvetica 9 bold")
        self.text.tag_configure("blue",foreground="blue")
 
        self.text.insert("end", self.dict["Title"],"blue") 
        self.text.insert("end", "\nOffered: ","bold", " ".join(self.dict["Offered"] )) 
        self.text.insert("end", "\nInstructor: ","bold", self.dict["Instructor"]) 
        self.text.insert("end", "\nRoom: ","bold", self.dict["Room"]) 
        self.text.insert("end", "\nDescription: ","bold", self.dict["Description"]) 

        self.text.configure(state='disabled',height = int(self.text.index('end').split('.')[0]) + 1)       
        self.text.pack(side = BOTTOM, anchor="w")

    def _change_mode(self, mode):
        if mode == "normal":
            self.label["bg"] = self.color1
            self.top_bar["bg"] = self.color1
            
            self.cur_color = self.color2

            if self.text != None:
                self.text["bg"] = self.color2 

        if mode == "hidden":
            self.label["bg"] = "#c7cdd6"
            self.top_bar["bg"] = "#c7cdd6"
            
            self.cur_color = "#e7eff8"

            if self.text != None:
                self.text["bg"] = "#e7eff8"

        if mode == "overlap":
            self.label["bg"] = "#ffc2cc"
            self.top_bar["bg"] = "#ffc2cc"
            
            self.cur_color = "#f8dee7"

            if self.text != None:
                self.text["bg"] = "#f8dee7"

    def remove_course_from_schedule(self):
        if(self.dict in current_classes):
            current_classes.remove(self.dict)
            
        self.destroy()
        draw_cal()
        draw_header()


    def toggle_show(self):   #Intermediate function to work with IntVar so courses can be serialized using json
        #FIXME add color changes to pane here (and maybe add_class_pane) so they update when classes are changed


        if self.var.get() == 0:
            self.dict["Showing"] = True
            self._change_mode("normal")
        else:
            self.dict["Showing"] = False
            self._change_mode("hidden")
            # change_wiget_color("#c7cdd6", cur_courses_pane.interior.nametowidget(course["Title"].lower()))
            
        update_overlap()
        draw_cal()
        draw_header()





def update_overlap():       #FIXME update so that this also controls the colors of the classes on the clander from draw_cal() method?
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
                        #TODO send out a notif to other panes that they are overlapped
                        try:
                            cur_courses_pane.interior.nametowidget(course["Title"].lower())._change_mode("overlap")
                            cur_courses_pane.interior.nametowidget(other["Title"].lower())._change_mode("overlap")
                        except:
                            pass
                
        


class SearchCourseElement(ttk.Frame):
    def __init__(self, parent,dict = None, color1 = "red", color2 = "green", *args, **kw):
        ttk.Frame.__init__(self, parent, *args , **kw)

        self.color1 = color1
        self.color2 = color2
        self.dict = dict
        self.text = None

        self.cur_color = color2

        self.top_bar = Frame(self, bg = color1)
        self.label = Label(self.top_bar, bg = color1, font = customtkinter.CTkFont(size=15, weight="normal"), width = 65, anchor = "nw")

        if not dict["Open"]:
            self.label["fg"] = "red"

        lbl_txt =("%-*s %-*s" % (15, " ".join(dict["Title"].split(" ")[0:2]), 15, dict["Credit"]))
        if dict["Open"]:
            lbl_txt += ("%-*s : %-*.*s" %      (6,"Open", 20, 8, ("(" + dict["Enrolled"] + "/" + dict["Capacity"] + ")")))
        else:
            lbl_txt += ("%-*s : %-*.*s" %     ( 6,"Closed", 20,20, ("(" + dict["Enrolled"] + "/" + dict["Capacity"] + ")")))
        lbl_txt += ("%-*s : %s" % (3, dict["Days"], time_to_str(dict["Start"]) + " - " + time_to_str(dict["End"])))
        self.label["text"] = lbl_txt

        customtkinter.CTkButton(self.top_bar, text = "Add",command=self.add_course_to_schedule, fg_color="#ff8b05", width = 50, height = 20, font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", padx = 5, pady = 2)
        customtkinter.CTkButton(self.top_bar, text = "Info", command = self.toggle_dropdown, fg_color="#0000FF", width = 50, height = 20,  font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", pady = 2)
        
        self.label.pack()
        self.top_bar.pack(side = TOP, anchor="w")
        self.pack(anchor="w")


    def toggle_dropdown(self):
        if self.text == None:
            self.make_text()
        else:
            self.text.destroy()
            self.text = None

    def make_text(self):        
        self.text = Text(self,  padx = 5, font="Helvetica 9", spacing1=5, wrap=WORD, width=101, bd = 0, bg = self.cur_color)
        self.text.tag_configure("bold", font="Helvetica 9 bold")
        self.text.tag_configure("blue",foreground="blue")
 
        self.text.insert("end", self.dict["Title"],"blue") 
        self.text.insert("end", "\nOffered: ","bold", " ".join(self.dict["Offered"] )) 
        self.text.insert("end", "\nInstructor: ","bold", self.dict["Instructor"]) 
        self.text.insert("end", "\nRoom: ","bold", self.dict["Room"]) 
        self.text.insert("end", "\nDescription: ","bold", self.dict["Description"]) 

        self.text.configure(state='disabled',height = int(self.text.index('end').split('.')[0]) + 1)       
        self.text.pack(side = BOTTOM, anchor="w")

    def add_course_to_schedule(self):
        if self.dict not in current_classes:
            current_classes.append(self.dict)

            if(len(current_classes) % 2 == 1):
                AddedCourseElement(cur_courses_pane.interior,self.dict, color1=color1, color2= bg1)
            else:
                AddedCourseElement(cur_courses_pane.interior,self.dict, color1=color2, color2= bg2)
            for day in self.dict["Days"]:
                draw_class( day, " ".join(self.dict["Title"].split(" ")[0:3]), self.dict["Start"], color = "blue")
        update_overlap()
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


# def make_text(parent, dict):
#     text = Text(parent,  font="Helvetica 9", spacing1=5, wrap=WORD, height = 12, width=55, bd = 0)
#     text.tag_configure("r", font="Helvetica 9")
#     text.tag_configure("bold", font="Helvetica 9 bold")
#     text.tag_configure("blue",foreground="blue")
#     text.tag_configure("red",foreground="red")

#     text.insert("end", dict["Title"] + "\n","blue") 
#     text.insert("end", "                                                " + dict["Term"] + "\n", "bold" ) 
#     text.insert("end", "Days: ","bold", str("".join(dict["Days"])), "r","   Start: ", "bold", time_to_str(dict["Start"]), "r", "  End: ","bold", ( time_to_str(dict["End"])), "r",  "                Credit: " + dict["Credit"] + "\n", 'red')
#     text.insert("end", "Enrolled: ","bold", dict["Enrolled"] + '/' + dict["Capacity"] + "\n") 
#     text.insert("end", "Instructor: ","bold", dict["Instructor"] + "\n") 
#     text.insert("end", "Room: ","bold", dict["Room"] + "\n") 
#     text.insert("end", "Description: ","bold", dict["Description"] + "\n") 
#     text.insert("end", "Offered: ","bold", " ".join(dict["Offered"])) 

#     # print(int(text.count("1.0", "end", "displaylines")[0] / 50.0))
#     # print(int(text.index('end-1c').split('.')[0]))
#     text.configure(state="disabled")
#     text.pack()
    

# def create_search_result_pane(dict):
#     f=Frame(result_courses_pane.interior,  relief= GROOVE, bd=3, bg = "white")
#     make_text(f,dict)
#     Button(f, text="Add to Schedule", height = 1, command=lambda *args: add_course_to_schedule(dict)).pack(side = BOTTOM, anchor="se", padx = 4, pady = 4)
#     f.pack(pady = 5)



        



#FIXME find out how to use tags to easily locate panes for different courses
# def create_added_class_pane(dict):
#     f=Frame(cur_courses_pane.interior,  relief= GROOVE, bd=3, bg = "white", name = dict["Title"].lower())
#     make_text(f,dict)
#     Button(f, text="Remove from Schedule", height = 1, command=lambda *args: remove_course_from_schedule(dict, f)).pack(side = RIGHT, anchor="se", padx = 4, pady = 4)

#     var = tkinter.IntVar()
#     var.set(int(not dict["Showing"]))
#     Checkbutton(f, text = "Hide Class", anchor = "w", variable=var, command=lambda *args: toggle_show(dict, var), relief=RIDGE, bd = 2).pack( side =LEFT,  anchor="sw", padx = 4, pady = 4)    
#     f.pack(pady = 5)

#     toggle_show(dict, var)

# def create_modern_search_courses_frame(dict, i):
#     f = Frame(result_courses_pane.interior)
 
#     lbl_txt =("%-*s %-*s" % (15, " ".join(dict["Title"].split(" ")[0:2]), 15, dict["Credit"]))

#     if dict["Open"]:
#         lbl_txt += ("%-*s : %-*.*s" %      (6,"Open", 20, 8, ("(" + dict["Enrolled"] + "/" + dict["Capacity"] + ")")))
#     else:
#         lbl_txt += ("%-*s : %-*.*s" %     ( 6,"Closed", 20,20, ("(" + dict["Enrolled"] + "/" + dict["Capacity"] + ")")))

#     lbl_txt += ("%-*s : %s" % (3, dict["Days"], time_to_str(dict["Start"]) + " - " + time_to_str(dict["End"])))


#     l = Label(f, text = lbl_txt, font = customtkinter.CTkFont(size=15, weight="normal"), width = 65, anchor = "nw")

#     if(not dict["Open"]):
#         l["fg"] = "red"


#     if i % 2 == 0:
#         l["bg"] = color1
#         f["bg"] = bg1
#     else:
#         l["bg"] = color2
#         f["bg"] = bg2

#     # Button(f, text = "Add", font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n")
#     customtkinter.CTkButton(f, text = "Add", command=lambda *args: add_course_to_schedule(dict), fg_color="#ff8b05", width = 50, height = 20, font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", padx = 5, pady = 2)

#     # Button(f, text = "Info", command = lambda *args: toggle_drop_down(f, dict), font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n")
#     customtkinter.CTkButton(f, text = "Info",  fg_color="#0000FF", width = 50, height = 20, command = lambda *args: toggle_drop_down(f, dict), font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", pady = 2)
    
     
    
#     l.pack()
#     f.pack(anchor="w")

# #FIXME new function
# def create_modern_added_courses_frame(dict, i):
#     f = Frame(cur_courses_pane.interior, name = dict["Title"].lower())
 
#     lbl_txt =("%-*s %-*s" % (15, " ".join(dict["Title"].split(" ")[0:2]), 15, dict["Credit"]))

#     if dict["Open"]:
#         lbl_txt += ("%-*s : %-*.*s" %      (6,"Open", 20, 8, ("(" + dict["Enrolled"] + "/" + dict["Capacity"] + ")")))
#     else:
#         lbl_txt += ("%-*s : %-*.*s" %     ( 6,"Closed", 20,20, ("(" + dict["Enrolled"] + "/" + dict["Capacity"] + ")")))

#     lbl_txt += ("%-*s : %s" % (3, dict["Days"], time_to_str(dict["Start"]) + " - " + time_to_str(dict["End"])))


#     l = Label(f, text = lbl_txt, font = customtkinter.CTkFont(size=15, weight="normal"), width = 65, anchor = "nw")
#     if i % 2 == 0:
#         l["bg"] = color1
#         f["bg"] = bg1
#     else:
#         l["bg"] = color2
#         f["bg"] = bg2


#     #TODO change this to an if statement for chosen courses page
#     var = tkinter.IntVar()
#     var.set(int(not dict["Showing"]))
#     Checkbutton(f, text = "Hide Class", variable=var, command=lambda *args: toggle_show(dict, var), font = customtkinter.CTkFont(size=10, weight="normal"), relief=RIDGE, bd = 2).pack( side = RIGHT, anchor = "n", pady=2)   

#     # Button(f, text = "Add", font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n")
#     customtkinter.CTkButton(f, text = "Remove", command=lambda *args: remove_course_from_schedule(dict, f), fg_color="#ff8b05", width = 50, height = 20, font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", padx = 5, pady = 2)

#     # Button(f, text = "Info", command = lambda *args: toggle_drop_down(f, dict), font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n")
#     customtkinter.CTkButton(f, text = "Info",  fg_color="#0000FF", width = 50, height = 20, command = lambda *args: toggle_drop_down(f, dict), font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", pady = 2)
    
     
    
#     l.pack()
#     f.pack(anchor="w")


# def toggle_drop_down(f, dict):
#     for child in f.winfo_children():
#         if "text" in child.winfo_name():
#             child.destroy()
#             return
        
#     if f["bg"] == bg1:
#         make_text2(f, dict, bg1)
#     else:
#         make_text2(f, dict, bg2)


# def make_text2(parent, dict, color ):
#     text = Text(parent,  font="Helvetica 9", spacing1=5, wrap=WORD, width=75, bd = 0, name = "text", bg = color)
#     text.tag_configure("r", font="Helvetica 9")
#     text.tag_configure("bold", font="Helvetica 9 bold")
#     text.tag_configure("blue",foreground="blue")
#     text.tag_configure("red",foreground="red")

#     text.insert("end", dict["Title"],"blue") 
#     # text.insert("end", "    " + dict["Term"] + "\n", "bold" ) 
#     text.insert("end", "\n", "bold" ) 

#     text.insert("end", "Offered: ","bold", " ".join(dict["Offered"] )+ "\n") 

#     text.insert("end", "Instructor: ","bold", dict["Instructor"] + "\n") 
#     text.insert("end", "Room: ","bold", dict["Room"] + "\n") 
#     text.insert("end", "Description: ","bold", dict["Description"] + "\n") 


#     text.configure(state='disabled')
#     text.configure(height = int(text.index('end').split('.')[0]) + 1)
    
#     text.pack(side = BOTTOM)





# def remove_course_from_schedule(course, frame):
#     global plan
#     if(course in current_classes):
#         current_classes.remove(course)
#         frame.destroy()
#     draw_cal()
#     draw_header()




# def toggle_show(course, var):   #Intermediate function to work with IntVar so courses can be serialized using json
#     #FIXME add color changes to pane here (and maybe add_class_pane) so they update when classes are changed
#     if var.get() == 0:
#         course["Showing"] = True
#     else:
#         course["Showing"] = False
#         change_wiget_color("#c7cdd6", cur_courses_pane.interior.nametowidget(course["Title"].lower()))
        
#     update_overlap()
#     draw_cal()
#     draw_header()





# def change_wiget_color(color, widget):
#     widget["bg"] = color

#     for child in widget.winfo_children():
#         if child.winfo_children():
#             # child has children, go through its children
#             change_wiget_color(color, child)
#         elif type(child) is Label:
#             child["bg"] = color

#         elif type(child) is Frame:
#             child["bg"] = color

#         elif type(child) is Text:
#             child["bg"] = color
#         else:
#             pass






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
                # TODO maybe change background pane to pink for classes that are overlapping?
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


    create_rounded_square(plan, x,y, 80 , lengthOff, color)


    plan.create_text(x + 4, y + 2, anchor="nw", text = title, fill  = 'white',font=("helvetica",10) )
    plan.create_text(x + 4, y + 15, anchor="nw", text = timeStr, fill  = 'white',font=("helvetica",8))


#TODO / FIXME update to aa circle
def create_rounded_square(canvas, x, y, width, height, color, r = 10):
    canvas.create_rectangle(x + r,y,x +width - r ,y + height + 1, fill = color,width = 0)   # vertical
    canvas.create_rectangle(x ,y + r ,x + width + 1,y + height - r, fill = color, width = 0) #horizontal

    canvas.create_oval(x , y , x + r * 2, y + r * 2, fill = color,width = 0) # top left
    canvas.create_oval(x + width - 2 * r, y, x + width, y + 2 * r, fill = color,width = 0) # top right
    canvas.create_oval(x, y + height - 2 * r, x + 2 * r, y + height, fill = color,width = 0) # bot left
    canvas.create_oval(x + width - 2 * r,  y + height - 2 * r, x + width,  y + height, fill = color,width = 0) # bot right




# Functions for changing display on pages           #FIXME error with page contents disappearing on deleating previous children
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
            SearchCourseElement(result_courses_pane.interior,loadData[entry], color1=color1, color2= bg1)  
        else:
            SearchCourseElement(result_courses_pane.interior,loadData[entry], color1=color2, color2= bg2)  


    # print(len(result_courses_pane.interior.winfo_children()))        


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
        reset_page()
        


def fetch(term, dept ="", type = "", courseName = ""):
    global result_courses_pane
    tabview.select(results)

    # result_courses_pane._clear_contents()
    # for c in result_courses_pane.interior.winfo_children():
    #         c.destroy()

    result_courses_pane.destroy()                               #FIXME quick hack for functionality
    result_courses_pane = VerticalScrolledFrame(results)
    result_courses_pane.pack()

    
    

    courseName = courseSelect.get("1.0",END)
    desc = titleSelect.get("1.0",END)

    if term in yearSelect.values and dept in subjectSelect.values and type in typeSelect.values:
        print("valid search")

        thread = threading.Thread(target=scrapeHTML, args=[term, dept, type,courseName,desc])
        thread.start()
        root.after(200, check_if_ready, thread)
    else:   #FIXME make this message better
        tkinter.messagebox.showerror(title="Search Box Error", message="INVALID SEARCH (make sure selected values are valid options)")
        print("INVALID SEARCH (make sure selected values are valid options)")
    




def scrapeHTML(term, dept ="", type = "", courseName = "", desc = ""):
    global loadData
    print("Finding courses...")

     #TODO make an actual element for searching
    textx = Label(result_courses_pane.interior, text = "Searching for results...", font = ("helvetica", 20)).pack()

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

    # browser.close()
    root.destroy()

#============================================ Set up the Tkinter window ============================================#
# Set up the root window for the app
print(time.strftime("%H:%M:%S", time.localtime()), "    -Creating GUI")

root = Tk()
root.title('UR Ready')  #Title for window
root.geometry("890x650")
root.option_add("*Font", ("Adobe Garamond Pro Bold", 10))
# root.configure(background=theme[0])

root.protocol("WM_DELETE_WINDOW", save_and_quit)

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

# Create an instance of ttk style
# s = ttk.Style()
# s.theme_use('default')
# s.configure('TNotebook.Tab', background=theme[1])
# s.map("TNotebook", background= [("selected", theme[1])])


tabview = ttk.Notebook(root,  height = 600, width = 400)
search = ttk.Frame(tabview)
results = ttk.Frame(tabview)
classes = ttk.Frame(tabview)
requirements = ttk.Frame(tabview)

tabview.add(search, text ='Search')
tabview.add(results, text ='Results')
tabview.add(classes, text ='Current Classes')
tabview.add(requirements, text ='Requirements')

tabview.pack(expand = 1, fill ="both")




#===================== Search Component =====================#

searchPane = Frame(search, width = 200, height = 100, relief=GROOVE, bd = 2)


styleT = ttk.Style()
styleT.configure('TCombobox', selectbackground=None, selectforeground=None)

searchLeft = Frame(searchPane)
searchRight = Frame(searchPane)

print(time.strftime("%H:%M:%S", time.localtime()), "    -Getting Combobox Values")
browser.get('https://cdcs.ur.rochester.edu/')


xmlSrc = lxml.html.fromstring(browser.page_source)

#FIXME add a function to verify that selected values are actually in the combobox

yearTitle = Label(searchLeft, text="Term (REQUIRED)", fg = "red").pack(anchor='w')
yearSelect = CustomCombobox(searchLeft,width = 32,values = (xmlSrc.xpath('//*[@id="ddlTerm"]/option/text()')),startingText="Semester (REQ) :")

yearSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
yearSelect.pack()



subjectTitle = Label(searchLeft, text="Subject:").pack(anchor='w')
subjectSelect = CustomCombobox(searchLeft, width = 32,values = (xmlSrc.xpath('//*[@id="ddlDept"]/option/text()')),startingText="Subject :")     # 
# subjectSelect.bind('<KeyRelease>', manage_combobox)
subjectSelect.bind("<<ComboboxSelected>>",lambda e: searchPane.focus())
subjectSelect.pack()


typeTitle = Label(searchLeft, text="Course Type:").pack(anchor='w')
typeSelect = CustomCombobox(searchLeft,width = 32,  values = (xmlSrc.xpath('//*[@id="ddlTypes"]/option/text()')),startingText="Type :")

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






#===================== Results Component =====================#



scrolingPane = Frame(results, bd=0, width = 400)

scroll_next = Button(scrolingPane, text="Next", command=next_page, anchor="ne",).pack(side = RIGHT)
scroll_prev = Button(scrolingPane, text="Prev", command=prev_page, anchor="nw").pack(side = LEFT)

scroll_text = Label(scrolingPane, text="Showing " + str(indxS) + "-" + str(indxE) + " of " + str(numResults), font=("Helvetica 10 bold"))
scroll_text.pack(side = TOP, padx = 100)

scrolingPane.pack()

result_courses_pane = VerticalScrolledFrame(results)
result_courses_pane.pack()
# scrolingPane.pack()




#===================== Current Courses Component =====================#

cur_courses_pane = VerticalScrolledFrame(classes)


cur_courses_pane.pack()

# Load all of the current saved clsses into the scroll pane     FIXME create a scrolling pane for this window
for entry in range(0,len(current_classes)):

    if entry % 2 == 0:
        AddedCourseElement(cur_courses_pane.interior,current_classes[entry], color1=color1, color2= bg1) 
    else:
        AddedCourseElement(cur_courses_pane.interior,current_classes[entry], color1=color2, color2= bg2) 



print(time.strftime("%H:%M:%S", time.localtime()), "    -Starting Program")
root.mainloop()



