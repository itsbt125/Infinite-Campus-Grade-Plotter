import json
import os
import plotly.graph_objects as go
from collections import defaultdict
from downloader import fetch_grades

def load_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Could not find '{file_path}'.")
        return None
    with open(file_path, 'r') as f:
        return json.load(f)

def process_enrollment(enrollment):
    enrollment_id = enrollment.get('enrollmentID', 'Unknown')
    subjects = defaultdict(lambda: defaultdict(list))
    valid_terms = set()
    all_scores = []
    
    for term in enrollment.get('terms', []):
        term_name = term.get('termName', 'Unknown Term')
        term_has_grades = False
        
        for course in term.get('courses', []):
            course_name = course.get('courseName', 'Unknown Course')
            
            for task in course.get('gradingTasks', []):
                if not task.get('hasAssignments'):
                    continue
                try:
                    grade = float(task.get('progressScore'))
                    subjects[course_name][term_name].append(grade)
                    all_scores.append(grade)
                    term_has_grades = True
                except (TypeError, ValueError):
                    continue
        
        if term_has_grades:
            valid_terms.add(term_name)
            
    return enrollment_id, subjects, sorted(valid_terms), all_scores

def create_plot(enrollment_id, subjects, valid_terms, all_scores):
    fig = go.Figure()
    colors = [
        '#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', 
        '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'
    ]
    
    point_map = defaultdict(list)
    for course_name, term_data in subjects.items():
        terms = [t for t in valid_terms if t in term_data]
        for t in terms:
            avg_score = sum(term_data[t]) / len(term_data[t])
            point_map[(t, avg_score)].append((course_name, term_data[t]))
    
    for idx, (course_name, term_data) in enumerate(subjects.items()):
        terms = [t for t in valid_terms if t in term_data]
        scores = [sum(term_data[t]) / len(term_data[t]) for t in terms]
        hover_texts = []
        for t, avg_score in zip(terms, scores):
            overlapping_courses = point_map[(t, avg_score)]
            tooltip_lines = []
            for oc_name, oc_grades in overlapping_courses:
                if len(oc_grades) > 1:
                    grades_str = ", ".join([f"{g:g}" for g in oc_grades])
                    tooltip_lines.append(f"<b>{oc_name}</b>: {avg_score:.1f}% [{grades_str}]")
                else:
                    tooltip_lines.append(f"<b>{oc_name}</b>: {avg_score:.1f}%")
            hover_texts.append("<br>".join(tooltip_lines))
        
        marker_colors = ['red' if s < 90 else colors[idx % len(colors)] for s in scores]
        is_flat_100 = len(scores) > 0 and all(s == 100 for s in scores)
        
        fig.add_trace(go.Scatter(
            x=terms,
            y=scores,
            mode='lines+markers',
            name=course_name,
            hovertext=hover_texts,
            hoverinfo='text',
            visible='legendonly' if is_flat_100 else True,
            line=dict(width=3, shape='spline', smoothing=0.3, color=colors[idx % len(colors)]),
            marker=dict(size=9, color=marker_colors, line=dict(width=1.5, color='white'))
        ))
    
    min_score = max(min(all_scores) - 5, 0) if all_scores else 0
    max_score = min(max(all_scores) + 2, 102) if all_scores else 102
    
    fig.update_layout(
        title=dict(text=f'<b>Grade Plotter</b><br><sup>Infinite Campus ID: {enrollment_id}</sup>', font=dict(size=22)),
        xaxis_title='<b>Quarter</b>',
        yaxis_title='<b>Grade (%)</b>',
        yaxis=dict(range=[min_score, max_score], gridcolor='rgba(230, 230, 230, 0.8)', zeroline=False),
        xaxis=dict(gridcolor='rgba(230, 230, 230, 0.8)', zeroline=False),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='closest',
        legend=dict(title="<b>Courses</b>", bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='rgba(200,200,200,0.5)', borderwidth=1,
                    yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(l=60, r=150, t=80, b=60)
    )
    
    fig.show()

def main():
    file_path = 'grades.json'
    usr = int(input("Enter your username: \n"))
    pwd = str(input("Enter your password: \n"))
    loc = str(input("Enter district location (check docs if needed): \n"))
    base_url = str(input("Enter base URL (check docs if needed): \n"))
    resp = fetch_grades(base_url,usr,pwd,loc)
    if resp  == "grades.json":
        data = load_data(file_path)
    else: 
        print(f"Failed with return data of: {resp}")
    
    if data:
        for enrollment in data:
            enrollment_id, subjects, valid_terms, all_scores = process_enrollment(enrollment)
            if subjects:
                create_plot(enrollment_id, subjects, valid_terms, all_scores)
            else:
                print(f"Skipping Enrollment {enrollment_id}: No valid grading data found.")

if __name__ == "__main__":
    main()
