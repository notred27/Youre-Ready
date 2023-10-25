import json
from tkinter import*
from tkinter import ttk
import json

from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


day_lookup = {"M":"Monday", "T":"Tuesday", "W":"Wednesday", "R":"Thursday", "F":"Friday", "S":"Saturday", "U":"Sunday"}
current_classes = json.loads(open("saved_classes.json", "r").read())



class VerticalScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
 
        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0, 
                                width = 800, height = 500,
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







class ModernCourseElement(ttk.Frame):
    def __init__(self, parent,dict = None, type = "g",mode=FALSE , *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

       
        self.dict = dict
        self.type = type
        self.mode = mode
        self.showing = True

        if type == "b":
            self.add_img = btn_b_add
            self.info_img = btn_b_info
            self.banner_img = banner_b
            self.body_img = body_b
            self.bg_color = "#ADD8E5"
        elif type == "o":
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
        self.remove_img = btn_remove_img

        self.canvas = Canvas(self, bg = "#FFFFFF",height = 54,width = 680,bd = 0,highlightthickness = 0,relief = "ridge")
        self.canvas.create_rectangle(0,0,681.0,54,fill="#EDEDED",outline="")
        self.draw_banner()

                
        self.btn_info = Button(self.canvas,image=self.info_img,   borderwidth=0,highlightthickness=0,command = lambda *args: self.toggle_dropdown(),relief="flat")
        self.btn_info.place(in_=self.canvas,x=579.0,y=7.0,width=95.0,height=21.0)#width and height are 2 less than they should be: hack to fix white border on click #FIXME

        if mode:
            self.btn_add = Button(self.canvas,image=self.add_img,borderwidth=0,highlightthickness=0,command = lambda: print("Add btn clicked"),relief="flat")
            self.btn_add.place(in_=self.canvas,x=507.0,y=7.0,width=52.0,height=21.0) #width and height are 2 less than they should be: hack to fix white border on click #FIXME
        else:   #TODO make these rely on local values, not the global ones
            self.btn_remove = Button(self.canvas,image=self.remove_img,borderwidth=0,highlightthickness=0,command = lambda: print("Remove btn clicked"),relief="flat")
            self.btn_remove.place(in_=self.canvas,x=507.0,y=7.0,width=62.0,height=21.0) #width and height are 2 less than they should be: hack to fix white border on click #FIXME

            self.btn_show = Button(self.canvas,image=self.show_img,borderwidth=0,highlightthickness=0,command = lambda: self.toggle_show(),relief="flat")
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
        self.canvas.create_text(14.0,9.0,anchor="nw",text=" ".join(self.dict["Title"].split(" ")[0:2]),fill="#FFFFFF",font=("IstokWeb Bold", 16 * -1, "bold"))

        days = []
        for d in self.dict["Days"]:
            days.append(day_lookup[d])

        self.canvas.create_text(170.0,9.0,anchor="nw",text=("/".join(days) + ": " + time_to_str(self.dict["Start"]) + " - " + time_to_str(self.dict["End"])),fill="#FFFFFF",font=("IstokWeb Bold", 14 * -1, "bold"))

        self.canvas.create_text(20.0,30.0,anchor="nw",text=self.dict["Credit"] + " credits",fill="#FFFFFF",font=("IstokWeb Bold", 10 * -1, "bold"))

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
        if self.showing:
            self.btn_show.config(image=self.hide_img)
        else:
            self.btn_show.config(image=self.show_img)

        self.showing = not self.showing
        #TODO add the other functionality

    def _change_mode(self, mode):   #change later to update which images are used
        pass



root = Tk()
root.title('UR Ready')  #Title for window
root.geometry("890x650")
root.option_add("*Font", ("Adobe Garamond Pro Bold", 10))

# tabposition = ttk.Style()
# tabposition.configure('TNotebook', sticky='w', tabposition='sw',borderwidth=0,  highlightthickness = 0)
# tabposition.layout("Tab",
# [('Notebook.tab', {'sticky': 'nswe', 'children':
#     [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
#             [('Notebook.label', {'side': 'top', 'sticky': ''})],})],})])




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
    file=relative_to_assets("hide_g.png"))
btn_remove_img = PhotoImage(
    file=relative_to_assets("remove_g.png"))


search_up  = PhotoImage(
    file=relative_to_assets("search_up.png"))
res_up  = PhotoImage(
    file=relative_to_assets("res_up.png"))
sch_up = PhotoImage(
    file=relative_to_assets("sch_up.png"))
req_up  = PhotoImage(
    file=relative_to_assets("req_up.png"))

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




# cur_courses_pane = VerticalScrolledFrame(root)
# cur_courses_pane.pack()






tabposition = ttk.Style()
tabposition.configure('TNotebook', sticky='w', tabposition='nw',borderwidth=0,  highlightthickness = 0, bd = 0,tabmargins = 0)
tabposition.configure('TNotebook.tab', sticky='w', tabposition='nw',borderwidth=0,  highlightthickness = 0, bd = 0,tabmargins = 0, relif = SOLID)

tabposition.layout("Tab",
[('Notebook.tab', {'sticky': 'nswe', 'children':
    [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
            [('Notebook.label', {'side': 'top', 'sticky': ''})],})],})])
tabposition.configure('TNotebook.Tab', padding=(0, 0, 0, 0))


# style=ttk.Style()
# style.layout("TNotebook", [])
# style.configure("TNotebook", highlightbackground="#848a98",tabmargins=0)# borderwidth = 0, highlightthickness = 0)



# Create style used by default for all Frames
# tabposition.configure('TFrame', background='#FFECDC', style = "TNotebook")


tabview = ttk.Notebook(root,  height = 600, width = 400)






# print(len(current_classes))
# # Load all of the current saved clsses into the scroll pane     FIXME create a scrolling pane for this window

# for entry in range(0,3):

#     if current_classes[entry]["Open"]:
#         if entry % 2 == 0:
#             ModernCourseElement(cur_courses_pane.interior, dict=current_classes[entry], type = "b")
#         else: 
#             ModernCourseElement(cur_courses_pane.interior, dict=current_classes[entry], type = "o")

#     else:
#         ModernCourseElement(cur_courses_pane.interior, dict=current_classes[entry])



# classes = ttk.Frame(tabview)
# requirements = ttk.Frame(tabview, )

# tabview.add(search, image=search_img)
# tabview.add(results, image = results_img)
# tabview.add(classes, image=schedule_img)
# tabview.add(requirements, image = requirements_img)

# tabview.pack(expand = 1, fill ="both")




class CustomTabview(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)
        self.frame_list = []
        self.btn_list = []
        self.btn_img_list = []

        self.tab_frame = Frame(self)
        self.current_frame = None
        self.content_frame = Frame(self)
        self.content_frame.pack_propagate(0)

        self.tab_frame.pack(side = TOP, anchor="nw", pady = 0)
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
        frame = Canvas(self.content_frame, name=id,  **kwargs)
        frame.create_image(0,0, image=tab_body, anchor="nw")

        
        # use  and index by tab
        i = len(self.frame_list) 
        tab = Button(self.tab_frame, text=id, borderwidth=0, highlightthickness=0, command=lambda: self.switch_tab(i))
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


    def add_element(self, elem, frame_name, x, y):
        elem.place(in_= self.get(frame_name), x = x, y = y)



    def get(self, id):
        for f in self.frame_list:
            if f.winfo_name() == id:
                return f
        return None

        
        

c = CustomTabview(root)
c.add_tab("search", width = 1000,height = 1000, btn_imgs=(search_up,search_down))
c.add_tab("results",width = 1000,height = 1000, btn_imgs=(res_up, res_down))
c.add_tab("schedual",width = 1000,height = 1000,btn_imgs=(sch_up, sch_down))
c.add_tab("requirements",width = 1000,height = 1000, btn_imgs=(req_up, req_down))


b = Button(root, text= "test button")
c.add_element(b, "results", 100, 100)

# b.pack(side = LEFT)


c.grid(row=0, column=0)






# notebook = Frame(root)
# notebook.pack(expand=True, fill='both', padx=5, pady=5)

# search = Frame(notebook, width = 100, bg = "red")
# search.pack_forget()

# result_courses_pane = VerticalScrolledFrame(search)
# result_courses_pane.pack()

# results = Frame(notebook)
# results.pack_forget()


# curren_tab = search

# tab1 = Button(notebook, text="Tab 1", command=lambda: switch_tab(search))
# tab2 = Button(notebook, text="Tab 2", command=lambda: switch_tab(results))

# tab1.pack(side="left", anchor="nw")
# tab2.pack(side="left", anchor="nw")

# search.pack(expand=True, fill='both')
# results.pack(expand=True, fill='both')

root.mainloop()



