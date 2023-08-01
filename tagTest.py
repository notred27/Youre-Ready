from tkinter import*
from tkinter import ttk
import tkinter
import json



current_classes = json.loads(open("saved_classes.json", "r").read())


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


def update_overlap():
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
            # add_class( day, " ".join(course["Title"].split(" ")[0:3]), course["Start"], color = "red")
            print(len(current_classes))

def remove_course(course, frame):
    global plan, num_credits_label, num_classes_label
    if(course in current_classes):
        current_classes.remove(course)
        frame.destroy()
    # draw_cal()
    print(len(current_classes))


bgColor = '#121212'
classParent = Tk()
# root.protocol("WM_DELETE_WINDOW", on_closing)
classParent.title('CDCS Visualizer')  #Title for window
classParent.geometry("890x650")



added_class_pane(current_classes[2])
added_class_pane(current_classes[5])
added_class_pane(current_classes[3])




classParent.mainloop()