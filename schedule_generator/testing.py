from collections import defaultdict

'''
# Initialize a defaultdict with a set as the default value
instructor_subjects = defaultdict(set)

# List of available instructors and their expertise
instructors = {
    'Instructor A': ['Math', 'Science'],
    'Instructor B': ['English', 'History'],
    'Instructor C': ['Math', 'English'],
}

# List of subjects to be assigned
subjects = ['Math', 'Science', 'English', 'History']

# Assign subjects based on expertise and subject limit
for subject in subjects:
    for instructor, expertise in instructors.items():
        if subject in expertise and len(instructor_subjects[instructor]) < 3:
            instructor_subjects[instructor].add(subject)
            break

# Output the assignments
for instructor, assigned_subjects in instructor_subjects.items():
    print(f"{instructor} is assigned to: {', '.join(assigned_subjects)}")

'''

i = 0
j = 0

for i in range(1, 5):
    for j in range(1, 35):
        print(f"CBE {i}{j:02}")
    