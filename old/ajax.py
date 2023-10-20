from requests import Session
import requests


session = Session()

# HEAD requests ask for *just* the headers, which is all you need to grab the
# session cookie
session.head('https://cdcs.ur.rochester.edu/')

response = session.post(
    url='https://cdcs.ur.rochester.edu/',
    data={
        'ddlTerm': 'D-Spring 2023',
        'ddlTypes': 'Lecture',
        'ddlDept': 'CIS'
    }
    
)


print(response.text)