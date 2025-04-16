**File Structure**

```bash
fittrack-webapp/
├── README.md  #README file for the project
├── TODO.md  #This file, lists all the TODOs
├── run.py  #The core Flask application file
├── requirements.txt  #Dependency list
├── app
│   ├── __init__.py  #Init of the website application
│   ├── routes.py  #Router of the templates
├── static  #Static files and resources
│   ├── css
│   ├── img
│   └── js
└── templates  #HTML templates
    ├── base.html  #Base template, shared with all the pages
    ├── index.html  #Intro page, namely view1
    ├── login.html  #Login page
    ├── register.html  #Register page
    ├── share.html  #Share page, namely view4
    ├── upload.html  #Upload page, namely view2
    └── visualise.html  #Visualise page, namely view3
```

**TODO**

- [ ] Improve the design of the website by using customised style including colour, format, shape etc.
- [ ] Add necessary information into the web page
- [ ] Decide the source of the data set
- [ ] Decide what kind of visualisation of the data and what visualisation lib we need
- [ ] Extent some new interesting features
