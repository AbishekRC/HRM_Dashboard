HRM Dashboard - Real-Time Industry Project 

🔗 LIVE DEMO 

🟢 Hosted on Render: https://hrm-dashboard-w0zd.onrender.com 
🎥 Demo Video:  

✅ KEY FEATURES 
->Dynamic Dashboard View 
	  - Flashcards: Active Employees, Attrited Employees, Attrition Rate 
	  - Interactive filters: Department, Year, Quarter, Location, Mode of Exit 
->Data Visualization (Plotly) 

-Pie,Bar, and Timeline charts for Onboarding and Attrition 

-Department wise attrition rate Comparison 

-Reason and Mode of Exit Analysis 
->Data Management 

-Add,Edit,Remove employee records via web interface 

-Search & manage onboarding data 

-Upload latest Excel file directly via Web UI 
->Excel Backend 
	-Uses Excel(.xlsx) sheets (onboarding,attrition) as the data source 

-Avoids the need for complex databases or paid tools 
 

TECHNOLOGIES USED 

Backend -Python Flask 

UI - HTML, Bootstrap 

Charts -Plotly.js 

Data Storage -Microsoft Excel 

Server -Gunicorn 

Deployment -Render.com 

🗂️ FOLDER STRUCTURE 
. 
├── data/ 
│   └── employee_data_v1.0.xlsx 
├── templates/ 
│   ├── index.html 
│   ├── add_employee.html 
│   ├── remove_employee.html 
│   ├── manage.html 
│   ├── edit_employee.html 
│   └── upload.html 
├── static/ 
│   └── styles.css (optional) 
├── app.py 
├── requirements.txt 
└── README.md 
 

🚀 SETUP & RUN LOCALLY 

 
1. Clone the repository: 
   git clone https://github.com/yourusername/HRM_Dashboard.git 
   cd HRM_Dashboard 
2. Create a virtual environment & activate it: 
   python -m venv venv 
   source venv/bin/activate  # macOS/Linux 
   venv\Scripts\activate   # Windows 
3. Install dependencies: 
   pip install -r requirements.txt 
4. Run the Flask server: 
   python app.py 
 

 

 

🌍 DEPLOYMENT GUIDE (RENDER) 

 
1. Ensure the following files exist: 
   - app.py 
   - requirements.txt 
   - Optional: Procfile with web: gunicorn app:app 
2. Connect GitHub repository to Render.com 
3. Select "Web Service" → Choose your repo → Set build command: 
   pip install -r requirements.txt 
   Start command: 
   gunicorn app:app 
4. Render will build & deploy your app. You'll get a public URL. 

📁 SHEETS USED 

 
- onboarding: Emp_Code, Name, DoJ, Designation, Location, Department 
- attrition: Emp_Code, Name, DoR, Reason, Location, Department, Mode_of_Exit 

 USE CASE 

 
This project was developed for Chakradhara Aerospace and Cargo Pvt Ltd as part of a live internship initiative to replace Excel-based manual HR tracking with a real-time, web-enabled dashboard. It demonstrates how data visualization, lightweight infrastructure, and Excel compatibility can be combined to create a smart, cost-efficient HR solution.(NOTE: THE DATAS USED ARE DERIVED FROM THE ORGINAL SOURCE AND MANIPULATED AS A MOCK DATASET, IT DOESNT CONTAIN ANY POTENTIAL COMPANY DATA WHICH IS PRIVATE AND CONFIDENTIAL) 
 

  

CONTACT 

 
Developer: Abishek Ravichandran. 
Role: HR Analyst Intern | MBA Student 
Email: abishekravichandranoff@gmail.com 
LinkedIn: https://www.linkedin.com/in/abisheksr29/ 

⭐ GIVE A STAR 

If you found this project insightful or useful, please consider giving it a ⭐ on GitHub! 
