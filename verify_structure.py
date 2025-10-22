import csv
from collections import defaultdict

# Read CSV data
with open('Dataset - Progress page test - Sheet2.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Check if there are any descriptions that repeat within the same student-topic combo
student_topic_desc = defaultdict(lambda: defaultdict(list))

for row in rows:
    student_id = row['student_id']
    topic = row['name']
    description = row['description']

    student_topic_desc[(student_id, topic)][description].append(row)

# Find descriptions with more than 1 question
print("Checking for descriptions with multiple questions (frequency > 1):")
found_multi = False
for (student_id, topic), descriptions in student_topic_desc.items():
    for description, questions in descriptions.items():
        if len(questions) > 1:
            found_multi = True
            print(f"Student {student_id}, Topic '{topic}', Description '{description}': {len(questions)} questions")

if not found_multi:
    print("No descriptions with multiple questions found - each description appears once per topic per student")

# Verify data integrity
print("\n=== Data Integrity Check ===")
print(f"Total rows: {len(rows)}")
print(f"Unique students: {len(set(row['student_id'] for row in rows))}")
print(f"Students: {sorted(set(row['student_id'] for row in rows))}")

# Check each student's data
for student_id in sorted(set(row['student_id'] for row in rows)):
    student_rows = [row for row in rows if row['student_id'] == student_id]
    topics = set(row['name'] for row in student_rows)
    mistakes = len([row for row in student_rows if row['Mistake?'].lower() == 'y'])

    print(f"\nStudent {student_id}:")
    print(f"  Total questions: {len(student_rows)}")
    print(f"  Topics: {len(topics)}")
    print(f"  Mistakes: {mistakes}")
    print(f"  Accuracy: {((len(student_rows) - mistakes) / len(student_rows) * 100):.1f}%")

    # Show topics with question counts
    topic_counts = defaultdict(int)
    for row in student_rows:
        topic_counts[row['name']] += 1

    print(f"  Topic breakdown:")
    for topic in sorted(topic_counts.keys()):
        print(f"    - {topic}: {topic_counts[topic]} questions")
