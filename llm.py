import json

prompt = (
    "Write at least 5 clear sentences addressed directly to the student in a neutral, matter-of-fact tone. "
    "Start with a concise summary of overall performance without exaggerated or overly positive language "
    "(avoid words like 'excellent', 'fantastic', 'great', 'wonderful'). "
    "Highlight at most 2–3 subjects showing meaningful improvements or declines between quarters, including small changes. "
    "Show all grades as whole numbers with a percent sign (e.g., 98%). "
    "Simplify course names by removing numbers, dashes, and extra descriptors "
    "Describe changes concisely without listing multiple quarters (e.g., 'increased from 94% to 99%' or 'decreased from 92% to 91%'). "
    "For subjects not mentioned, note that grades remained steady. "
    "Do not include filler, repetition, or forward-looking encouragement. Keep the response compact and focused strictly on performance."
)

def generate_plot_json(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    summary = []
    for enrollment in data:
        enrollment_summary = {"quarters": {}}
        for term in enrollment.get('terms', []):
            term_name = term.get('termName', 'Unknown Term')
            term_summary = {}
            for course in term.get('courses', []):
                course_name = course.get('courseName', 'Unknown Course')
                course_name = ''.join([c for c in course_name if not c.isdigit()]).strip()
                grades = []
                for task in course.get('gradingTasks', []):
                    if not task.get('hasAssignments'):
                        continue
                    try:
                        grades.append(float(task.get('progressScore')))
                    except (TypeError, ValueError):
                        continue
                if grades:
                    term_summary[course_name] = f"{round(sum(grades) / len(grades))}%"
            if term_summary:
                enrollment_summary["quarters"][term_name] = term_summary
        if enrollment_summary["quarters"]:
            summary.append(enrollment_summary)
    full_prompt = {
        "grades": summary,
        "prompt": prompt
    }
    return full_prompt

if __name__ == "__main__":
    payload = generate_plot_json("grades.json")
    with open("prompt.txt", "w") as f:
        json.dump(payload, f, indent=2)
    print("Saved full prompt to prompt.txt")
