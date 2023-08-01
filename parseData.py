import json


data3 = ["Course Course Title Term Credits Status", 
        "CSC 161-1 Introduction to Programming Spring 2023 4.0 Open",
          "Schedule:", 
          "Day Begin End Location Start Date End Date",
            "TR 1650 1805 Hoyt Hall Room 104 01/11/2023 05/06/2023", 
            "Enrollment: Enrolled     ", 
            "188 Capacity     ", 
            "200", 
            "Instructors: Andrew Read-McFarland", 
            "Description: Hands-on introduction to programming using the Python programming language. Covers basic programming constructs including statements, expressions, variables, conditionals, iteration, and functions, as well as object-oriented programming and graphics.", 
            "This course is for non-majors, and/or students with less math and science background. Lab and workshop required.", 
            "This course may not be used for CSC major credit if completed after or at the same time as CSC171", 
            "Offered: Fall Spring Summer", 
            "Books Click to buy books for this course from the bookstore"]   

data2 = ["Course Course Title Term Credits Status",
         "CSC 999-21 Doctoral Dissertation Spring 2023 Thesis Open", 
         "Schedule:", 
         "Day Begin End Location Start Date End Date", 
         "Enrollment: Enrolled     ", 
         "1 Capacity     ",
           "30", 
           "Instructors: Gonzalo Mateos Buckstein", 
           "Description: Blank Description",
           "Offered: Fall Spring Summer", 
             "Books Click to buy books for this course from the bookstore"]   

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


    for item in data:
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




# data.remove("Course Course Title Term Credits Status")

# title_term_credit_statis = data[0]
# del data[0]

# data.remove("Schedule:")
# data.remove("Day Begin End Location Start Date End Date")

# day_hour_room = data[0]
# del data[0]

# data.remove("Enrollment: Enrolled     ")

# enrolled = data[0]
# del data[0]

# capacity = data[0]
# del data[0]

# instructor = data[0]
# del data[0]

# description = data[0]
# del data[0]


# data.remove("Books Click to buy books for this course from the bookstore")

# offered = data[-1]
# del data[-1]


#restrictions = data


def print_dict(dict):
    for i in dict:
        print( i + " : " + str(dict[i] ))


# print_dict(make_course(data))
# print()
# print_dict(make_course(data2))


# load = open("scraped_classes.json", "r")
# loadData = json.loads(load.read())

print(float("4.0"))
