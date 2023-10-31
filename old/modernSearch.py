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

current_classes = json.loads(open("saved_classes.json", "r").read())



class VerticalScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
 
        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0, 
                                width = 800, height = 300,
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


def make_text(parent, dict):
    text = Text(parent,  font="Helvetica 9", spacing1=5, wrap=WORD, height = 12, width=55, bd = 0)
    text.tag_configure("r", font="Helvetica 9")
    text.tag_configure("bold", font="Helvetica 9 bold")
    text.tag_configure("blue",foreground="blue")
    text.tag_configure("red",foreground="red")

    text.insert("end", dict["Title"] + "\n","blue") 
    text.insert("end", "                                                " + dict["Term"] + "\n", "bold" ) 
    text.insert("end", "Days: ","bold", str("".join(dict["Days"])), "r","   Start: ", "bold", time_to_str(dict["Start"]), "r", "  End: ","bold", ( time_to_str(dict["End"])), "r",  "                Credit: " + dict["Credit"] + "\n", 'red')
    text.insert("end", "Enrolled: ","bold", dict["Enrolled"] + '/' + dict["Capacity"] + "\n") 
    text.insert("end", "Instructor: ","bold", dict["Instructor"] + "\n") 
    text.insert("end", "Room: ","bold", dict["Room"] + "\n") 
    text.insert("end", "Description: ","bold", dict["Description"] + "\n") 
    text.insert("end", "Offered: ","bold", " ".join(dict["Offered"])) 

    # print(int(text.count("1.0", "end", "displaylines")[0] / 50.0))
    # print(int(text.index('end-1c').split('.')[0]))
    text.configure(state="disabled")
    text.pack()

def make_text2(parent, dict, color ):
    text = Text(parent,  font="Helvetica 9", spacing1=5, wrap=WORD, width=75, bd = 0, name = "text", bg = color)
    text.tag_configure("r", font="Helvetica 9")
    text.tag_configure("bold", font="Helvetica 9 bold")
    text.tag_configure("blue",foreground="blue")
    text.tag_configure("red",foreground="red")

    text.insert("end", dict["Title"],"blue") 
    # text.insert("end", "    " + dict["Term"] + "\n", "bold" ) 
    text.insert("end", "\n", "bold" ) 

    text.insert("end", "Offered: ","bold", " ".join(dict["Offered"] )+ "\n") 

    text.insert("end", "Instructor: ","bold", dict["Instructor"] + "\n") 
    text.insert("end", "Room: ","bold", dict["Room"] + "\n") 
    text.insert("end", "Description: ","bold", dict["Description"] + "\n") 


    text.configure(state='disabled')
    text.configure(height = int(text.index('end').split('.')[0]) + 1)
    
    text.pack(side = BOTTOM)


def create_added_class_pane(dict):
    f=Frame(cur_courses_pane.interior,  relief= GROOVE, bd=3, bg = "white", name = dict["Title"].lower())
    make_text(f,dict)
    Button(f, text="Remove from Schedule", height = 1).pack(side = RIGHT, anchor="se", padx = 4, pady = 4)

    var = tkinter.IntVar()
    var.set(int(not dict["Showing"]))
    Checkbutton(f, text = "Hide Class", anchor = "w", variable=var, relief=RIDGE, bd = 2).pack( side =LEFT,  anchor="sw", padx = 4, pady = 4)    
    f.pack(pady = 5)

    # toggle_show(dict, var)

root = Tk()
root.title('UR Ready')  #Title for window
root.geometry("890x650")
root.option_add("*Font", ("Adobe Garamond Pro Bold", 10))


def toggle_drop_down(f, dict):
    for child in f.winfo_children():
        if "text" in child.winfo_name():
            child.destroy()
            return
        
    if f["bg"] == bg1:
        make_text2(f, dict, bg1)
    else:
        make_text2(f, dict, bg2)


class AddedCourseElement(ttk.Frame):
    def __init__(self, parent,dict = None, color1 = "red", color2 = "green", *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

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


        Checkbutton(self.top_bar, text = "Hide Class",  font = customtkinter.CTkFont(size=10, weight="normal"), relief=RIDGE, bd = 2).pack( side = RIGHT, anchor = "n", padx = 3, pady=2)   
        customtkinter.CTkButton(self.top_bar, text = "Remove", fg_color="#ff8b05", width = 50, height = 20, font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", padx = 5, pady = 2)
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




def create_modern_frame(dict, i):
    f = Frame(cur_courses_pane.interior)
 
    lbl_txt =("%-*s %-*s" % (15, " ".join(dict["Title"].split(" ")[0:2]), 15, dict["Credit"]))

    if dict["Open"]:
        lbl_txt += ("%-*s : %-*.*s" %      (6,"Open", 20, 8, ("(" + dict["Enrolled"] + "/" + dict["Capacity"] + ")")))
    else:
        lbl_txt += ("%-*s : %-*.*s" %     ( 6,"Closed", 20,20, ("(" + dict["Enrolled"] + "/" + dict["Capacity"] + ")")))

    lbl_txt += ("%-*s : %s" % (3, dict["Days"], time_to_str(dict["Start"]) + " - " + time_to_str(dict["End"])))


    l = Label(f, text = lbl_txt, font = customtkinter.CTkFont(size=15, weight="normal"), width = 65, anchor = "nw")
    if i % 2 == 0:
        l["bg"] = color1
        f["bg"] = bg1
    else:
        l["bg"] = color2
        f["bg"] = bg2


    #TODO change this to an if statement for chosen courses page
    Checkbutton(f, text = "Hide Class",  font = customtkinter.CTkFont(size=10, weight="normal"), relief=RIDGE, bd = 2).pack( side = RIGHT, anchor = "n", pady=2)   

    # Button(f, text = "Add", font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n")
    customtkinter.CTkButton(f, text = "Add", fg_color="#ff8b05", width = 50, height = 20, font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", padx = 5, pady = 2)

    # Button(f, text = "Info", command = lambda *args: toggle_drop_down(f, dict), font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n")
    customtkinter.CTkButton(f, text = "Info",  fg_color="#0000FF", width = 50, height = 20, command = lambda *args: toggle_drop_down(f, dict), font = customtkinter.CTkFont(size=10, weight="normal")).pack(side = RIGHT, anchor="n", pady = 2)
    
     
    
    l.pack()
    f.pack(anchor="w")

color1 = "#fcfc5d"
bg1 = "#f5f5bf"
color2 = "#5ec1ff"
bg2 = "#c5e6fa"

cur_courses_pane = VerticalScrolledFrame(root)


cur_courses_pane.pack()

# Load all of the current saved clsses into the scroll pane     FIXME create a scrolling pane for this window
for entry in range(0,5):
    # create_modern_frame(current_classes[entry], entry) 

    if entry % 2 == 0:
        a = AddedCourseElement(cur_courses_pane.interior, dict=current_classes[entry], color1=color1, color2= bg1)
        # a._change_mode("hidden")

        # a._change_mode("normal")
    else:
        AddedCourseElement(cur_courses_pane.interior, dict=current_classes[entry], color1=color2, color2= bg2)



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


lst =  json.loads(open("dropbox_info.json", "r").read())["Dept"]



CustomCombobox(root, width= 20,values=lst, startingText="Semester (REQ) :").pack()


Entry(root, width = 15).pack()

CustomCombobox(root, width= 15,values=lst, startingText="Starts after:").pack()
CustomCombobox(root, width= 15,values=lst, startingText="Starts before:").pack()




root.mainloop()