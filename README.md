# You're Ready!

This is an application to be used as a class selector for students at the University of Rochester. Many students have expressed their dissatisfaction with the 
university's current scheduling applications, and how different resources (such as schedule builders, class availability checkers, and class time offerings) 
are disconnected from each other. This application aims to connect all of these tasks together in one easy-to-use app!

# Features

### Current Class Availability

Easily search for classes by name, id, subject, course type, or other keywords! You can also choose to hide results for classes that have already been filled
to avoid mistakes in planning. This information is kept up-to-date by using U of R's public [Course Description / Course Schedule](https://cdcs.ur.rochester.edu/) 
database. 

### Group Courses Together

While current university tools separate different course sections, this application groups all sections together by semester so you can easily choose the best time 
for your schedule. No more sifting through pages upon pages of lab sections to search for a time that fits your needs. 

### Class Schedule Builder

Tired of not being able to immediately see if a new course will conflict with your other courses? Now chosen classes will pop up on a calendar side by side with the 
classes you can choose from! Any conflicting classes will cause courses to become red on the schedule. You can also save an image of your schedule by using the button in the upper right-hand corner. 

# Future Plans
Future features planned for this application include a way to save multiple schedules so you can plan out backups in case your selected classes get filled when 
registration opens, and further checks such as prerequisites and major requirements. Additionally, more quality-of-life changes such as improved UI and text
formatting are planned to improve the user's experience. 


# Project Description
This project was built by Michael Reidy using Python and the Tkinter and Selenium libraries. Tkinter was used to create the GUI for the project, and Selenium was used
to perform web scraping to keep the app's information up-to-date. While the standard Tkinter library provided a solid framework for constructing this project's GUI,
multiple custom widgets and images were used to make up for its outdated graphical design. Figma was used to create these new graphical elements. Data for this application is also stored in JSON files so the same schedule can be edited session after session. Error logging was also implemented to provide a way for users to send feedback if any errors are encountered. 

# Important
_**This application requires Firefox to work.**_ This is because a headless Firefox browser is used for scraping data. Additionally, this application is in no way 
officially affiliated with the University of Rochester and is only intended to be used recreationally. Finally, all of the data in this application should be as
up-to-date as possible, but any information on this application is not guaranteed to be accurate. This project was inspired by a [proposed UI redesign of a 
similar college website.](https://medium.com/joinforge/course-registration-made-simple-lous-list-ux-redesign-646bf15975d6)


