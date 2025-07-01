import io
#importing section
import plotly
#flask imports
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify ,send_file
#other lib imports
from plotly.utils import PlotlyJSONEncoder
from datetime import datetime
import pandas as pd
import plotly.graph_objs as go
import json
import os
app = Flask(__name__)
app.secret_key='hrm-secret-key' # for flashing messages
# Set the path to your Excel file
file_path = os.path.join('data', 'employee_data_v1.0.xlsx')
EXCEL_FILE = os.path.join('data', 'employee_data_v1.0.xlsx')
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
       if 'file' not in request.files:
           flash('No file part')
           return redirect(request.url)
       file = request.files['file']
       if file.filename == '':
           flash('No selected file')
           return redirect(request.url)
       if file and allowed_file(file.filename):
           file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'employee_data_v1.0.xlsx'))  # Always overwrite
           flash('File uploaded and replaced successfully.')
           return redirect(url_for('dashboard'))

   return render_template('upload.html')
@app.route('/')
def dashboard():
   # Get selected filters from query string
   dept_filter = request.args.get('Department')
   view_type = request.args.get('view', 'onboarding')  # default onboarding
   df_on = pd.read_excel(file_path, sheet_name='onboarding')
   df_attr = pd.read_excel(file_path, sheet_name='attrition')
   start_date_str = request.args.get('start_date', '')
   end_date_str = request.args.get('end_date', '')
   trend_view = request.args.get('trend_view', 'monthly')
   # Convert to datetime (only if value is provided)
   start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
   end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
   # Ensure date columns are parsed correctly
   if view_type == 'onboarding':
       df = pd.read_excel(file_path, sheet_name='onboarding')
       df.columns = df.columns.str.strip()
       df['DoJ'] = pd.to_datetime(df['DoJ'], errors='coerce')
       date_column = 'DoJ'
   else:
       df = pd.read_excel(file_path, sheet_name='attrition')
       df.columns = df.columns.str.strip()
       df['DoR'] = pd.to_datetime(df['DoR'], errors='coerce')
       date_column = 'DoR'
       if start_date:
           df = df[df[date_column] >= start_date]
       if end_date:
           df = df[df[date_column] <= end_date]
   #-----------------------------------
   # FLASH CARD DATA SECTION
   selected_dept = request.args.get('Department', '')
   selected_locs = request.args.getlist('location')
   total_attrited = df_attr.shape[0]
   # Year & Quarter Filtering
   quarter = request.args.get('quarter', '')
   selected_year = request.args.get('year', '')
   if view_type == 'onboarding':
       date_col = 'DoJ'
   else:
       date_col = 'DoR'
   df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
   years = sorted(df[date_col].dropna().dt.year.unique(), reverse=True)
   # 🔢 Flash Card Metrics Calculation
   total_onboarded_df = df_on[df_on['DoJ'].notna()]
   total_attrited_df = df_attr[df_attr['DoR'].notna()]
   # Apply filters to DataFrame copies, not integer values
   filtered_onboarded_df = total_onboarded_df.copy()
   filtered_attrited_df = total_attrited_df.copy()
   if selected_dept:
       filtered_onboarded_df = filtered_onboarded_df[filtered_onboarded_df['Department'] == selected_dept]
       filtered_attrited_df = filtered_attrited_df[filtered_attrited_df['Department'] == selected_dept]
   selected_mode = request.args.get('mode_of_exit', '')
   # ✅ Only filter by Mode_of_Exit if attrition view is active
   if view_type == 'attrition':
       filtered_attrited_df = df_attr.copy()
       if selected_mode:
           filtered_attrited_df = filtered_attrited_df[filtered_attrited_df['Mode_of_Exit'] == selected_mode]
   if selected_locs:
       filtered_onboarded_df = filtered_onboarded_df[filtered_onboarded_df['Location'].isin(selected_locs)]
       filtered_attrited_df = filtered_attrited_df[filtered_attrited_df['Location'].isin(selected_locs)]
   if selected_year:
       filtered_onboarded_df = filtered_onboarded_df[filtered_onboarded_df['DoJ'].dt.year == int(selected_year)]
       filtered_attrited_df = filtered_attrited_df[filtered_attrited_df['DoR'].dt.year == int(selected_year)]
   if quarter:
       q_map = {'Q1': [1, 2, 3], 'Q2': [4, 5, 6], 'Q3': [7, 8, 9], 'Q4': [10, 11, 12]}
       filtered_onboarded_df = filtered_onboarded_df[filtered_onboarded_df['DoJ'].dt.month.isin(q_map[quarter])]
       filtered_attrited_df = filtered_attrited_df[filtered_attrited_df['DoR'].dt.month.isin(q_map[quarter])]
   # Filter by year
   if selected_year:
       df = df[df[date_col].dt.year == int(selected_year)]
   # Filter by quarter
   if quarter:
       month_map = {
           'Q1': [1, 2, 3],
           'Q2': [4, 5, 6],
           'Q3': [7, 8, 9],
           'Q4': [10, 11, 12],
       }
       df = df[df[date_col].dt.month.isin(month_map.get(quarter, []))]
   # Filter by Quarter
   if quarter:
       if view_type == 'onboarding':
           date_col = 'DoJ'
       else:
           date_col = 'DoR'
       df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
       if quarter == 'Q1':
           df = df[df[date_col].dt.month.isin([1, 2, 3])]
       elif quarter == 'Q2':
           df = df[df[date_col].dt.month.isin([4, 5, 6])]
       elif quarter == 'Q3':
           df = df[df[date_col].dt.month.isin([7, 8, 9])]
       elif quarter == 'Q4':
           df = df[df[date_col].dt.month.isin([10, 11, 12])]
   # Filtered Dataa
   filtered_onboarded = df.shape[0]
   filtered_attrited = df_attr[df_attr['Department'] == selected_dept].shape[0] if selected_dept else total_attrited
   filtered_active = df[~df['Emp_Code'].isin(df_attr['Emp_Code'])].shape[0]
   filtered_attrition_rate = round((filtered_attrited / filtered_onboarded) * 100, 2) if filtered_onboarded > 0 else 0
   # Check if any filters are applied
   filters_applied = any([
       selected_year,
       quarter,
       selected_dept,
       selected_locs,
       selected_mode
   ])
   # ✅ Now assign counts safely
   active_employees = filtered_onboarded_df.shape[0]
   attrited_employees = filtered_attrited_df.shape[0]
   total_pool = active_employees + attrited_employees
   attrition_rate = (attrited_employees / total_pool * 100) if total_pool > 0 else 0
   attrition_rate = round(attrition_rate, 2)

   # Set dynamic flashcard labels
   if filters_applied:
       onboarded_label = "New Joiners"
       attrited_label = "No. of Leavings"
       attrition_label = "Filtered Attrition Rate"
   else:
       onboarded_label = "Active Employees"
       attrited_label = "Attrited Employees"
       attrition_label = "Attrition Rate"
   #Calculating Average Tenure Before Resignation
   # STEP: Join onboarding and attrition to calculate tenure
   df_on_join = df_on[['Emp_Code', 'DoJ']].copy()
   df_attr_join = df_attr[['Emp_Code', 'DoR']].copy()
   df_attr = df_attr[df_attr['Department'].notna()]
   # Merge to get both DoJ and DoR for employees who have resigned
   df_joined = pd.merge(df_attr_join, df_on_join, on='Emp_Code', how='inner')
   # Parse to datetime (ensure proper format)
   df_joined['DoJ'] = pd.to_datetime(df_joined['DoJ'], errors='coerce')
   df_joined['DoR'] = pd.to_datetime(df_joined['DoR'], errors='coerce')
   # Drop any records with missing dates
   df_joined = df_joined.dropna(subset=['DoJ', 'DoR'])
   # Calculate tenure in days
   df_joined['TenureDays'] = (df_joined['DoR'] - df_joined['DoJ']).dt.days
   # Convert to months/years
   df_joined['TenureMonths'] = df_joined['TenureDays'] / 30  # approx.
   df_joined['TenureYears'] = df_joined['TenureDays'] / 365
   # Compute average tenure in years
   average_tenure_years = round(df_joined['TenureYears'].mean(), 2) if not df_joined.empty else 0
   # Get filter values
   view_type = request.args.get('view', 'onboarding')
   selected_dept = request.args.get('Department', '')
   selected_locs = request.args.getlist('location')
   print("loaded rows:",len(df_on),"onboarding",len(df_attr),"attribution")
   # filtering data & select correct sheet
   if view_type == 'onboarding':
       df = df_on.copy()
       title = 'Onboarding by Department'
   else:
       df = df_attr.copy()
       title = 'Attrition by Department'
   Departments = sorted(df['Department'].dropna().unique())
   locations = sorted(df['Location'].dropna().unique())
   if selected_dept:
       df = df[df['Department'] == selected_dept]
   if selected_locs:
       df = df[df['Location'].isin(selected_locs)]
   count_by_dept = df['Department'].value_counts()
   print("DataFrame Shape (After Filtering):", df.shape)
   print("Current View:", view_type)
   print("Columns:", df.columns)
   #charts------------------------------------------------------------------------->
   # Create trend_chart: joining or exit trend over time
   # Timeline chart: DoJ or DoL
   #CHART 1 (TREND CHART): DISPLAYS TREND CHART IN ONBOARDING OR ATTRITION BASED ON OPTION
   if view_type == 'onboarding':
       trend_df = df_on.copy()
       trend_df['Date'] = pd.to_datetime(trend_df['DoJ'], errors='coerce')
       # Apply filters to trend_df
       if selected_dept:
           trend_df = trend_df[trend_df['Department'] == selected_dept]
       if selected_locs:
           trend_df = trend_df[trend_df['Location'].isin(selected_locs)]
       if selected_year:
           trend_df = trend_df[trend_df['Date'].dt.year == int(selected_year)]
       if quarter:
           month_map = {'Q1': [1, 2, 3], 'Q2': [4, 5, 6], 'Q3': [7, 8, 9], 'Q4': [10, 11, 12]}
           trend_df = trend_df[trend_df['Date'].dt.month.isin(month_map[quarter])]
       # 📊 Group based on trend view
       if trend_view == 'quarterly':
           trend_df['Quarter'] = trend_df['Date'].dt.to_period('Q').astype(str)
           timeline_data = trend_df['Quarter'].value_counts().sort_index()
       else:  # monthly
           trend_df['Month'] = trend_df['Date'].dt.to_period('M').astype(str)
           timeline_data = trend_df['Month'].value_counts().sort_index()
       # Plotly chart
       timeline_chart = {
           'data': [go.Scatter(x=timeline_data.index.astype(str), y=timeline_data.values, mode='lines+markers')],
           'layout': go.Layout(title=f"{view_type.capitalize()} Trend Over Time ({trend_view.title()})",
                               xaxis_title='Time',
                               yaxis_title='Count')
       }
   else:
       trend_df = df_attr.copy()
       trend_df['Date'] = pd.to_datetime(trend_df['DoR'], errors='coerce')
   # Apply filters to trend_df
   if selected_dept:
       trend_df = trend_df[trend_df['Department'] == selected_dept]
   if selected_locs:
       trend_df = trend_df[trend_df['Location'].isin(selected_locs)]
   if selected_year:
       trend_df = trend_df[trend_df['Date'].dt.year == int(selected_year)]
   if quarter:
       month_map = {'Q1': [1, 2, 3], 'Q2': [4, 5, 6], 'Q3': [7, 8, 9], 'Q4': [10, 11, 12]}
       trend_df = trend_df[trend_df['Date'].dt.month.isin(month_map[quarter])]
   # 📊 Group based on trend view
   if trend_view == 'quarterly':
       trend_df['Quarter'] = trend_df['Date'].dt.to_period('Q').astype(str)
       timeline_data = trend_df['Quarter'].value_counts().sort_index()
   else:  # monthly
       trend_df['Month'] = trend_df['Date'].dt.to_period('M').astype(str)
       timeline_data = trend_df['Month'].value_counts().sort_index()
   # Plotly chart
   timeline_chart = {
       'data': [go.Scatter(x=timeline_data.index.astype(str), y=timeline_data.values, mode='lines+markers')],
       'layout': go.Layout(title=f"{view_type.capitalize()} Trend Over Time ({trend_view.title()})",
                           xaxis_title='Time',
                           yaxis_title='Count')
   }
#ATT CHART 2 (PIE CHART):ATTRITION BY DEPARTMENT CHART
   # Attrition Count by Department
   # Clone the attrition dataframe
   filtered_attr_df = df_attr.copy()
   # Apply Department filter if any
   if selected_dept:
       filtered_attr_df = filtered_attr_df[filtered_attr_df['Department'] == selected_dept]
   # Apply Location filter
   if selected_locs:
       filtered_attr_df = filtered_attr_df[filtered_attr_df['Location'].isin(selected_locs)]
   # Apply Year filter
   if selected_year:
       filtered_attr_df = filtered_attr_df[
           pd.to_datetime(filtered_attr_df['DoR'], errors='coerce').dt.year == int(selected_year)
           ]
   # Apply Quarter filter
   if quarter:
       month_map = {
           'Q1': [1, 2, 3],
           'Q2': [4, 5, 6],
           'Q3': [7, 8, 9],
           'Q4': [10, 11, 12]
       }
       filtered_attr_df = filtered_attr_df[
           pd.to_datetime(filtered_attr_df['DoR'], errors='coerce').dt.month.isin(month_map[quarter])
       ]
   #generating the chart
   if not filtered_attr_df.empty:
       attr_dept = filtered_attr_df['Department'].value_counts()
       attrition_chart = {
           'data': [go.Pie(labels=attr_dept.index, values=attr_dept.values)],
           'layout': go.Layout(title='Filtered Attrition by Department')
       }
   else:
       attrition_chart = {
           'data': [],
           'layout': go.Layout(title='No Attrition Data Available for Selected Filters')
       }

#ONB CHART 2 (BAR CHART): Onboarding Count by Department (chart shows department wise bar representation)
   # Step 1: Copy original onboarding data
   filtered_onboard_df = df_on.copy()

   # Step 2: Apply filters if any
   if selected_dept:
       filtered_onboard_df = filtered_onboard_df[filtered_onboard_df['Department'] == selected_dept]

   if selected_locs:
       filtered_onboard_df = filtered_onboard_df[filtered_onboard_df['Location'].isin(selected_locs)]

   if selected_year:
       filtered_onboard_df = filtered_onboard_df[
           pd.to_datetime(filtered_onboard_df['DoJ'], errors='coerce').dt.year == int(selected_year)
           ]

   if quarter:
       q_map = {'Q1': [1, 2, 3], 'Q2': [4, 5, 6], 'Q3': [7, 8, 9], 'Q4': [10, 11, 12]}
       filtered_onboard_df = filtered_onboard_df[
           pd.to_datetime(filtered_onboard_df['DoJ'], errors='coerce').dt.month.isin(q_map[quarter])
       ]

   # Step 3: Create filtered chart
   if not filtered_onboard_df.empty:
       onboard_dept = filtered_onboard_df['Department'].value_counts()
       onboarding_chart = {
           'data': [go.Bar(x=onboard_dept.index, y=onboard_dept.values)],
           'layout': go.Layout(title='Filtered Onboarding by Department')
       }
   else:
       onboarding_chart = {
           'data': [],
           'layout': go.Layout(title='No Onboarding Data Available for Selected Filters')
       }

   # 🔧 Prepare Reason Pie Chart using filtered attrition data
   reason_chart = {}

   if view_type == 'attrition':
       # Start with the base attrition dataset
       filtered_attrited_df = df_attr.copy()

       # ✅ Apply filters
       if selected_dept:
           filtered_attrited_df = filtered_attrited_df[filtered_attrited_df['Department'] == selected_dept]
       if selected_locs:
           filtered_attrited_df = filtered_attrited_df[filtered_attrited_df['Location'].isin(selected_locs)]

       filtered_attrited_df['DoR'] = pd.to_datetime(filtered_attrited_df['DoR'], errors='coerce')  # ✅ Ensure date
       if selected_year:
           filtered_attrited_df = filtered_attrited_df[filtered_attrited_df['DoR'].dt.year == int(selected_year)]
       if quarter:
           q_map = {'Q1': [1, 2, 3], 'Q2': [4, 5, 6], 'Q3': [7, 8, 9], 'Q4': [10, 11, 12]}
           filtered_attrited_df = filtered_attrited_df[filtered_attrited_df['DoR'].dt.month.isin(q_map[quarter])]

       # ✅ Create Pie Chart for Reason
       if not filtered_attrited_df.empty and 'Reason' in filtered_attrited_df.columns:
           reason_counts = filtered_attrited_df['Reason'].value_counts()

           if not reason_counts.empty:
               reason_chart = {
                   'data': [go.Pie(
                       labels=reason_counts.index,
                       values=reason_counts.values,
                       hole=0.4  # Donut hole - optional
                   )],
                   'layout': go.Layout(
                       title='Reasons for Attrition (Filtered)',
                       height=400,
                       margin=dict(t=50, b=50)
                   )
               }
           else:
               print("⚠️ No values in 'Reason' column after filtering.")
       else:
           print("⚠️ No 'Reason' column or no filtered data.")

   #ATT CHART 3(PIE CHART):,MODE OF EXIT CHART
   mode_exit_chart = {}
   if view_type == 'attrition' and not filtered_attrited_df.empty and 'Mode_of_Exit' in filtered_attrited_df.columns:
       mode_counts = filtered_attrited_df['Mode_of_Exit'].value_counts()
       if not mode_counts.empty:
           mode_exit_chart = {
               'data': [go.Pie(
                   labels=mode_counts.index,
                   values=mode_counts.values,
                   hole=0.4  # makes it a donut
               )],
               'layout': go.Layout(
                   title='Mode of Exit Distribution',
                   height=400
               )
           }
   #chart for comparable dept and table
   #changing here
   Departments_all = df_on['Department'].dropna().unique()
   dept_data = []
   for dept in Departments_all:
       onboarded = df_on[df_on['Department'] == dept]
       attrited = df_attr[df_attr['Department'] == dept]
       # Apply filters
       if selected_locs:
           onboarded = onboarded[onboarded['Location'].isin(selected_locs)]
           attrited = attrited[attrited['Location'].isin(selected_locs)]
       if selected_year:
           onboarded = onboarded[onboarded['DoJ'].dt.year == int(selected_year)]
           attrited = attrited[attrited['DoR'].dt.year == int(selected_year)]
       if quarter:
           q_map = {'Q1': [1, 2, 3], 'Q2': [4, 5, 6], 'Q3': [7, 8, 9], 'Q4': [10, 11, 12]}
           onboarded = onboarded[onboarded['DoJ'].dt.month.isin(q_map[quarter])]
           attrited = attrited[attrited['DoR'].dt.month.isin(q_map[quarter])]
       total_onboard = onboarded.shape[0]
       total_attrite = attrited.shape[0]
       total_pool = total_onboard + total_attrite
       attrition_rate = (total_attrite / total_pool) * 100 if total_pool > 0 else 0
       dept_data.append({
           'Department': dept,
           'onboarded': total_onboard,
           'attrited': total_attrite,
           'attrition_rate': round(attrition_rate, 2)
       })
   # Create DataFrame
   combined_df = pd.DataFrame(dept_data)
   # Pass to HTML table
   dept_table_data = combined_df.to_dict(orient='records')

   filtered_table_data = df.copy().head(100).to_dict(orient='records')  # optional: limit to 100 for performance
   # ---------------------
   return render_template(
       'index.html',
       onboarding_chart=json.dumps(onboarding_chart, cls=PlotlyJSONEncoder),
       attrition_chart=json.dumps(attrition_chart, cls=PlotlyJSONEncoder),
       timeline_chart=json.dumps(timeline_chart, cls=PlotlyJSONEncoder),
       trend_view=trend_view,
       reason_chart=json.dumps(reason_chart, cls=PlotlyJSONEncoder),
       Departments = Departments,
       selected_dept = selected_dept,
       view_type = view_type,
       locations = locations,
       selected_locs = selected_locs,
       start_date=start_date_str,
       end_date=end_date_str,
       total_onboarded=total_onboarded_df.shape[0],
       total_attrited=total_attrited_df.shape[0],
       selected_mode=selected_mode,
       total_active=active_employees,
       attrition_rate=filtered_attrition_rate,
       onboarded_label=onboarded_label,
       attrited_label=attrited_label,
       attrition_label=attrition_label,
       filtered_onboarded=filtered_onboarded,
       filtered_attrited=filtered_attrited,
       filtered_active=filtered_active,
       filtered_attrition_rate=filtered_attrition_rate,
       selected_year=selected_year,
       years=years,
       active_employees=active_employees,
       attrited_employees=attrited_employees,
       quarter=quarter,
       dept_table_data=dept_table_data,
       dept_attrition_data = dept_data,
       average_tenure = average_tenure_years,
       mode_exit_chart=json.dumps(mode_exit_chart, cls=PlotlyJSONEncoder),
       filtered_table_data=filtered_table_data

   )
@app.route('/add', methods=['GET', 'POST'])
def add_employee():
   file_path = os.path.join('data', 'employee_data_v1.0.xlsx')
   df_onboarding = pd.read_excel(file_path, sheet_name='onboarding')
   # Auto-generate next Emp_Code
   if not df_onboarding.empty:
       last_code = df_onboarding['Emp_Code'].astype(int).max()
       new_Emp_Code = str(last_code + 1)
   else:
       new_Emp_Code = "1001"
   # --- Suggest Emp_Code ---
   existing_codes = df_onboarding['Emp_Code'].astype(str).tolist()
   next_number = 1
   while True:
       suggested_code = f"EMP{next_number:03d}"
       if suggested_code not in existing_codes:
           break
       next_number += 1
   # Handle Form Submission
   if request.method == 'POST':
       # ✅ Use manual override if provided, otherwise use auto
       Emp_Code = request.form.get("manual_code") or request.form["Emp_Code"]
       Emp_Code = str(Emp_Code).strip()
       # ❌ Block duplicate Emp_Code
       if Emp_Code in df_onboarding['Emp_Code'].values:
           flash(f"❌ Emp_Code '{Emp_Code}' already exists.")
           return redirect('/add')
       name = request.form['Name']
       DoJ = request.form['DoJ']
       Department = request.form['Department']
       designation = request.form['Designation']
       location = request.form['Location']
       # --- Check for duplicate Emp_Code ---
       if Emp_Code in existing_codes:
           flash(f"Error: Emp_Code '{Emp_Code}' already exists. Please use a unique value.")
           return redirect('/add')
       new_entry = {
           'Emp_Code': Emp_Code,
           'Name': name,
           'DoJ': DoJ,
           'Department': Department,
           'Designation': designation,
           'Location': location
       }
       # Append and Save
       df_onboarding = pd.concat([df_onboarding, pd.DataFrame([new_entry])], ignore_index=True)
       with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
           df_onboarding.to_excel(writer, sheet_name='onboarding', index=False)
       flash(f"New employee '{name}' added successfully with Emp_Code: {Emp_Code}")
       return redirect('/add')
   df = pd.read_excel(EXCEL_FILE, sheet_name='onboarding')
   df['Emp_Code'] = df['Emp_Code'].astype(str).str.strip()
   # 🧮 Get the next Emp_Code
   if not df.empty:
       last_code = df['Emp_Code'].astype(int).max()
       new_Emp_Code = str(last_code + 1)
   else:
       new_Emp_Code = "1001"  # or whatever starting code you prefer
   # Render form with suggested code
   return render_template('add_employee.html', suggested_Emp_Code=suggested_code)
@app.route('/remove',methods=['GET','POST'])
def remove_employee():
   if request.method == 'POST':
       name_to_remove = request.form['name']
       df = pd.read_excel(file_path, sheet_name='attrition')
       # Debug log before
       print("🗑 Original Attrition Sheet:")
       print(df)
       # Remove employee
       df = df[df['Name'] != name_to_remove]
       # Debug log after
       print("✅ Updated Sheet After Removal:")
       print(df)
       # Save back to Excel
       with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
           df.to_excel(writer, sheet_name='Attrition', index=False)
       return redirect('/')
   return render_template('remove_employee.html')
def home():
   return "✅ Flask is working!"
@app.route('/manage', methods=['GET', 'POST'])
def manage_employees():
   df = pd.read_excel(EXCEL_FILE, sheet_name='onboarding')
   search_results = None
   keyword=""
   if request.method == 'POST':
       keyword = request.form['search'].strip().lower()
       search_results = df[df.apply(lambda row: keyword in str(row.values).lower(), axis=1)]
   return render_template('manage.html', results=search_results, search=keyword)
@app.route('/delete/<Emp_Code>')
def delete_employee(Emp_Code):
   df = pd.read_excel(EXCEL_FILE, sheet_name='onboarding')
   df = df[df['Emp_Code'] != Emp_Code]  # Remove matching Emp_Code
   with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
       df.to_excel(writer, sheet_name='onboarding', index=False)
   flash(f'Employee {Emp_Code} deleted successfully.')
   return redirect('/manage')
@app.route('/edit/<Emp_Code>', methods=['GET', 'POST'])
def edit_employee(Emp_Code):
   df = pd.read_excel(EXCEL_FILE, sheet_name='onboarding')
   df['Emp_Code'] = df['Emp_Code'].astype(str).str.strip()
   Emp_Code = str(Emp_Code).strip()
   # 🔍 Match the employee row
   matched_row = df[df['Emp_Code'] == Emp_Code]
   if matched_row.empty:
       flash(f"❌ Employee with Emp_Code '{Emp_Code}' not found.")
       return redirect('/manage')
   employee = matched_row.iloc[0]
   if request.method == 'POST':
       df.loc[df['Emp_Code'] == Emp_Code, 'Name'] = request.form['Name']
       df.loc[df['Emp_Code'] == Emp_Code, 'DoJ'] = request.form['DoJ']
       df.loc[df['Emp_Code'] == Emp_Code, 'Department'] = request.form['Department']
       df.loc[df['Emp_Code'] == Emp_Code, 'Designation'] = request.form['Designation']
       df.loc[df['Emp_Code'] == Emp_Code, 'Location'] = request.form['Location']
       with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
           df.to_excel(writer, sheet_name='onboarding', index=False)
       flash(f'Employee {Emp_Code} updated successfully.')
       return redirect('/manage')
   return render_template('edit_employee.html', employee=employee)
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
   query = request.args.get('q', '').lower()
   df = pd.read_excel(EXCEL_FILE, sheet_name='onboarding')
   names = df['Name'].dropna().unique()
   matches = [name for name in names if query in name.lower()]
   return jsonify(matches)
if __name__ == '__main__':
   app.run(debug=True)