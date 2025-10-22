import csv
import json

# Read CSV and get basic statistics
with open('Dataset - Progress page test - Sheet2.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Get unique student IDs
student_ids = set(row['student_id'] for row in rows)
print(f"Unique student IDs: {sorted(student_ids)}")
print(f"Total number of students: {len(student_ids)}")
print(f"Total number of rows: {len(rows)}")

# Show sample data structure
print("\nFirst row:")
print(json.dumps(rows[0], indent=2))

# Get unique topics for first student
first_student_id = sorted(student_ids)[0]
topics = set(row['name'] for row in rows if row['student_id'] == first_student_id)
print(f"\nTopics for student {first_student_id}:")
for topic in sorted(topics):
    print(f"  - {topic}")
