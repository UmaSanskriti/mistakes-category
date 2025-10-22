import csv
import json
from collections import defaultdict

# Read CSV data
with open('Dataset - Progress page test - Sheet2.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Organize data structure: student -> topic -> description -> questions
data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

for row in rows:
    student_id = row['student_id']
    topic = row['name']
    description = row['description']

    # Store question data
    question_data = {
        'answer_id': row['answer_id'],
        'q_text': row['q_text1'] or row['q_text'],
        'q_image': row['q_image'],
        'model_solution': row['model solution'],
        'student_answer': row['student answer'],
        'maximum_mark': row['maximum mark'],
        'mark_awarded': row['mark_awarded'],
        'mistake': row['Mistake?'],
        'skill_level': row['skill level']
    }

    data[student_id][topic][description].append(question_data)

# Calculate statistics for topics
topic_stats = {}
for student_id in data:
    topic_stats[student_id] = {}
    for topic in data[student_id]:
        total_questions = 0
        mistakes = 0
        skill_levels = []

        for description in data[student_id][topic]:
            for question in data[student_id][topic][description]:
                total_questions += 1
                if question['mistake'].lower() == 'y':
                    mistakes += 1
                if question['skill_level']:
                    skill_levels.append(int(question['skill_level']))

        accuracy = ((total_questions - mistakes) / total_questions * 100) if total_questions > 0 else 0
        avg_skill_level = sum(skill_levels) / len(skill_levels) if skill_levels else 0

        topic_stats[student_id][topic] = {
            'total_questions': total_questions,
            'mistakes': mistakes,
            'accuracy': accuracy,
            'skill_level': avg_skill_level
        }

# Now let's identify mistake categories
# We'll extract mistake categories from descriptions for questions with mistakes
mistake_categories = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

for student_id in data:
    for topic in data[student_id]:
        for description in data[student_id][topic]:
            mistake_category = description  # The description IS the mistake category
            for question in data[student_id][topic][description]:
                if question['mistake'].lower() == 'y':
                    mistake_categories[student_id][topic][description][mistake_category].append(question)
                else:
                    # Also include non-mistakes for complete question list
                    mistake_categories[student_id][topic][description][mistake_category].append(question)

# Generate HTML
html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Attempts and Mistake Categories</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .student-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }

        .student-header {
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }

        .student-header h2 {
            color: #667eea;
            font-size: 2rem;
        }

        .topic-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
        }

        .topic-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }

        .topic-title {
            color: #2d3748;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .topic-stats {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .stat-badge {
            background: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .skill-level {
            color: #667eea;
        }

        .total-questions {
            color: #3182ce;
        }

        .accuracy {
            color: #38a169;
        }

        .description-section {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .description-title {
            color: #4a5568;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }

        .pills-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .mistake-pill {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .mistake-pill:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .frequency-badge {
            background: rgba(255,255,255,0.3);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.7);
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .modal-content {
            background-color: white;
            margin: 2% auto;
            padding: 0;
            border-radius: 20px;
            width: 90%;
            max-width: 1000px;
            max-height: 90vh;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideIn 0.3s;
        }

        @keyframes slideIn {
            from {
                transform: translateY(-50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-header h2 {
            font-size: 1.5rem;
        }

        .close {
            color: white;
            font-size: 35px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
            transition: transform 0.2s;
        }

        .close:hover {
            transform: scale(1.1);
        }

        .modal-body {
            padding: 30px;
            max-height: calc(90vh - 100px);
            overflow-y: auto;
        }

        .question-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }

        .question-card:last-child {
            margin-bottom: 0;
        }

        .question-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }

        .question-number {
            font-weight: 700;
            color: #667eea;
            font-size: 1.1rem;
        }

        .marks-badge {
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-weight: 600;
            font-size: 0.9rem;
        }

        .question-section {
            margin-bottom: 15px;
        }

        .section-label {
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 8px;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .section-content {
            background: white;
            padding: 12px;
            border-radius: 8px;
            line-height: 1.6;
        }

        .question-image {
            max-width: 100%;
            border-radius: 8px;
            margin-top: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .student-answer {
            border-left: 3px solid #fc8181;
        }

        .model-solution {
            border-left: 3px solid #68d391;
        }

        .scrollbar::-webkit-scrollbar {
            width: 10px;
        }

        .scrollbar::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        .scrollbar::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 10px;
        }

        .scrollbar::-webkit-scrollbar-thumb:hover {
            background: #764ba2;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.8rem;
            }

            .student-header h2 {
                font-size: 1.5rem;
            }

            .topic-title {
                font-size: 1.2rem;
            }

            .topic-header {
                flex-direction: column;
                align-items: flex-start;
            }

            .modal-content {
                width: 95%;
                margin: 5% auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Student Attempts & Mistake Categories</h1>
"""

# Generate content for each student
for student_id in sorted(data.keys()):
    html += f"""
        <div class="student-section">
            <div class="student-header">
                <h2>Student ID: {student_id}</h2>
            </div>
"""

    # Generate content for each topic
    for topic in sorted(data[student_id].keys()):
        stats = topic_stats[student_id][topic]
        html += f"""
            <div class="topic-section">
                <div class="topic-header">
                    <h3 class="topic-title">{topic}</h3>
                    <div class="topic-stats">
                        <span class="stat-badge skill-level">Skill Level: {stats['skill_level']:.1f}</span>
                        <span class="stat-badge total-questions">Questions: {stats['total_questions']}</span>
                        <span class="stat-badge accuracy">Accuracy: {stats['accuracy']:.1f}%</span>
                    </div>
                </div>
"""

        # Generate content for each description
        for description in sorted(data[student_id][topic].keys()):
            questions = data[student_id][topic][description]

            # Count frequency of this mistake category (description) within this topic-description combo
            # Since each description section shows one mistake category (the description itself),
            # the frequency is the number of questions in this description
            frequency = len(questions)

            # Create unique ID for modal
            modal_id = f"modal_{student_id}_{topic}_{description}".replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace('*', '').replace('&', '').replace('/', '').replace('-', '_')

            html += f"""
                <div class="description-section">
                    <div class="description-title">{description}</div>
                    <div class="pills-container">
                        <div class="mistake-pill" onclick="openModal('{modal_id}')">
                            <span class="frequency-badge">{frequency}x</span>
                            <span>{description}</span>
                        </div>
                    </div>
                </div>
"""

        html += """
            </div>
"""

    html += """
        </div>
"""

# Generate modals for each description
for student_id in sorted(data.keys()):
    for topic in sorted(data[student_id].keys()):
        for description in sorted(data[student_id][topic].keys()):
            questions = data[student_id][topic][description]
            modal_id = f"modal_{student_id}_{topic}_{description}".replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace('*', '').replace('&', '').replace('/', '').replace('-', '_')

            html += f"""
<div id="{modal_id}" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2>{description}</h2>
            <span class="close" onclick="closeModal('{modal_id}')">&times;</span>
        </div>
        <div class="modal-body scrollbar">
"""

            # Add each question
            for idx, question in enumerate(questions, 1):
                html += f"""
            <div class="question-card">
                <div class="question-header">
                    <span class="question-number">Question {idx}</span>
                    <span class="marks-badge">{question['mark_awarded']}/{question['maximum_mark']} marks</span>
                </div>

                <div class="question-section">
                    <div class="section-label">Question</div>
                    <div class="section-content">
                        {question['q_text']}
"""
                if question['q_image']:
                    html += f"""
                        <img src="{question['q_image']}" alt="Question Image" class="question-image" onerror="this.style.display='none'">
"""
                html += """
                    </div>
                </div>

                <div class="question-section">
                    <div class="section-label">Student Answer</div>
                    <div class="section-content student-answer">
"""
                html += question['student_answer'] if question['student_answer'] else "<em>No answer provided</em>"
                html += """
                    </div>
                </div>

                <div class="question-section">
                    <div class="section-label">Model Solution</div>
                    <div class="section-content model-solution">
"""
                html += question['model_solution'] if question['model_solution'] else "<em>No model solution available</em>"
                html += """
                    </div>
                </div>
            </div>
"""

            html += """
        </div>
    </div>
</div>
"""

# Add JavaScript and closing tags
html += """
    </div>

    <script>
        function openModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
            document.body.style.overflow = 'hidden';
        }

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
            document.body.style.overflow = 'auto';
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        }

        // Close modal with Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const modals = document.getElementsByClassName('modal');
                for (let modal of modals) {
                    if (modal.style.display === 'block') {
                        modal.style.display = 'none';
                        document.body.style.overflow = 'auto';
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

# Write HTML file
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Website generated successfully: index.html")
print(f"Total students: {len(data)}")
print(f"Student IDs: {sorted(data.keys())}")
