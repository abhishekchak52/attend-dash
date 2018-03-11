from requests_html import HTMLSession
import pandas as pd
from tqdm import tqdm


url = 'http://apf.ststephens.edu/attendance_stku2018'
get_semester_url = 'http://apf.ststephens.edu/getsemesterbypro?programme_id={}'
get_month_url = 'http://apf.ststephens.edu/getmonthbysemepro?semester_id={}&programme_id={}'


def scrape_attendance():
   
    session = HTMLSession()
    r = session.get(url) 
    course_options = r.html.find('option')[1:33]
    session.close()
    programs = {  course.attrs['value'] : course.text
            for course in course_options }
    all_attendance = []
    for program in tqdm(programs, desc='Program'):
        df = scrape_course(program, programs)
        all_attendance.append(df)
    attendance_df = pd.concat(all_attendance)
    return tidy_scraped(attendance_df)
        
    
def scrape_course(programme_id,programs_dict):
    session = HTMLSession()
    p = session.get(get_semester_url.format(programme_id))
    sem_dict = p.json()
    
    if sem_dict['status']:
        semesters = {}
        for entry in sem_dict['semester']:
            semesters[entry['semester_id']] = entry['name']
    semesters_attendance = []
    for semester in tqdm(semesters,desc = 'Semester', leave=False):
        try:
            semesters_attendance.append(
                scrape_semester(
                    programme_id=programme_id,
                    semester_id=semester,
                    semesters_dict=semesters,
                    programs_dict=programs_dict,
                    html_session = session
                )
            )
        except ValueError:
            pass
    total_attendance = pd.concat(semesters_attendance)
    session.close()
    return total_attendance

    
def scrape_semester(programme_id, semester_id, semesters_dict, programs_dict, html_session):
    
    q = html_session.get(get_month_url.format(semester_id,programme_id))
    month_dict = q.json()
    
    if month_dict['status'] and month_dict['month'] != []:
        months = {}
        for entry in month_dict['month']:
            months[entry['month_no']] = entry['name']   
    months_attendance = []
    for month in tqdm(months,desc='Month', leave=False):
        try:
            months_attendance.append(
                scrape_month(
                    programme_id=programme_id,
                    semester_id=semester_id, 
                    month_id=month, 
                    months_dict=months, 
                    semesters_dict=semesters_dict,
                    programs_dict = programs_dict,
                    html_session = html_session
                )
            )
        except ValueError:
            pass
    semester_attendance = pd.concat(months_attendance)
    return semester_attendance

def scrape_month(programme_id, semester_id, month_id, months_dict, semesters_dict,programs_dict,html_session):
    payload = {
        'programme' : programme_id,
        'semester' : semester_id,
        'month' : month_id
    }
    
    s = html_session.post(url, data=payload)
    if s.status_code == 200: # A OK
        try:
            scraped_table = pd.read_html(s.html.html, header=1)[0] # Read the table into Pandas
        except ValueError:
            raise
        # Perform some formatting to get it into order
        scraped_table.drop(columns=scraped_table.columns.values.tolist()[-11:], inplace=True)
        scraped_table['Month'] = months_dict[payload['month']]
        scraped_table['Semester'] = semesters_dict[payload['semester']]
        scraped_table['Year'] = programs_dict[payload['programme']].split(' ')[0]
        scraped_table['Course'] = ' '.join(programs_dict[payload['programme']]
                                           .split(' ')[2:]
                                          ).replace('B. A. HONOURS ','').replace('B. SC. HONOURS ','')
        # Identify papers and name columns accordingly
        papers = [
            paper.text 
            for paper in s.html.find(selector='th') 
            if 'colspan' in paper.attrs and paper.attrs['colspan'] == '6'
        ]
        types = ['Lectures_Held', 'Lectures_Attended',
                 'Tutorials_Held','Tutorials_Attended',
                 'Practicals_Held', 'Practicals_Attended',]
        headers = ['Name']
        for paper in papers:
            for attendance_type in types:
                headers.append(paper+'_'+attendance_type)     
        headers.extend(['Month', 'Semester', 'Year', 'Course'])
        col_names = scraped_table.columns.values.tolist()
        col_rename = dict(zip(col_names,headers))
        scraped_table.rename(mapper=col_rename, axis=1,inplace=True)
        return scraped_table
    else:
        return None
    

def tidy_scraped(scraped_table):
    scraped_melted = pd.melt(scraped_table,id_vars=['Name', 'Month', 'Semester','Year','Course'], var_name='Paper_Attendance')
    paper_types = scraped_melted['Paper_Attendance'].str.split('_')
    paper_names = paper_types.str.get(0)
    class_type = paper_types.str.get(1)
    attendance_type = paper_types.str.get(2)
    scraped_melted['Paper Name'] = paper_names
    scraped_melted['Class Type'] = class_type
    scraped_melted['Attendance Type'] = attendance_type
    scraped_melted.drop('Paper_Attendance', axis =1, inplace=True)
    attend_tidy = scraped_melted.pivot_table(
        index=['Year','Course','Name', 'Semester','Paper Name', 'Month', 'Class Type'],
        columns='Attendance Type',
        values='value'
    )
    attend_tidy['Percent'] = (attend_tidy['Attended']/attend_tidy['Held']*100).round(2)
    attend_tidy.dropna(axis=0, how='any', inplace=True)
    return attend_tidy

if __name__=="__main__":
    df = scrape_attendance()
    df.to_pickle('scraped_data.pkl')
    