import csv
from collections import defaultdict

# Read CSV data
with open('Dataset - Progress page test - Sheet2.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Find descriptions with multiple questions
print("Descriptions with multiple questions in the same student-topic:\n")

student_topic_desc = defaultdict(lambda: defaultdict(list))

for row in rows:
    student_id = row['student_id']
    topic = row['name']
    description = row['description']

    student_topic_desc[(student_id, topic)][description].append(row)

# Find any with multiple questions
found = False
for (student_id, topic), descriptions in sorted(student_topic_desc.items()):
    for description, questions in sorted(descriptions.items()):
        if len(questions) > 1:
            found = True
            print(f"Student {student_id}, Topic '{topic}', Description '{description}':")
            print(f"  Number of questions: {len(questions)}")
            for i, q in enumerate(questions, 1):
                print(f"  Q{i}: Mistake={q['Mistake?']}, Marks={q['mark_awarded']}/{q['maximum mark']}")
            print()

if not found:
    print("No descriptions found with multiple questions in the same student-topic combination.")
    print("\nThis means each description within a topic for a student has exactly 1 question.")
    print("The frequency count in the website represents the number of questions per description (which is 1 for all cases).")
