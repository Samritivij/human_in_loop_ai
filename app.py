from flask import Flask, render_template, request, redirect, jsonify, url_for
from ai_agent import get_answer_from_kb, add_to_knowledge_base, load_knowledge_base
from help_requests import get_all_requests, add_help_request, resolve_request, mark_timeouts_as_unresolved
import os
import json
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', feedback_submitted=False)

@app.route('/ask', methods=['POST'])
def ask():
    try:
        question = request.form['question']
        answer = get_answer_from_kb(question)
        if answer:
            return render_template('index.html', question=question, answer=answer)
        else:
            add_help_request(question)
            return render_template('index.html', question=question, answer="No answer found. Sent to supervisor.")
    except Exception as e:
        return render_template('index.html', answer=f"An error occurred: {str(e)}")

@app.route('/requests')
def view_requests():
    mark_timeouts_as_unresolved()
    pending = get_all_requests()
    return render_template('requests.html', requests=pending)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    try:
        question = request.form['question']
        answer = request.form['answer']
        add_to_knowledge_base(question, answer)
        resolve_request(question, ai_suggestion=answer)
        print(f"Follow-up: Question '{question}' has been resolved with answer: {answer}")
        return redirect('/kb')
    except Exception as e:
        return f"Error submitting answer: {str(e)}", 500

@app.route('/kb')
def view_kb():
    query = request.args.get('query', '').lower()
    kb = load_knowledge_base()

    if query:
        filtered_kb = [entry for entry in kb if query in entry['question'].lower() or query in entry['answer'].lower()]
    else:
        filtered_kb = kb

    return render_template('kb.html', kb=filtered_kb, query=query)

@app.route('/suggest_edit', methods=['POST'])
def suggest_edit():
    try:
        question = request.form['question']
        suggestion = request.form['suggestion']
        suggestion_entry = {
            "question": question,
            "suggestion": suggestion,
            "timestamp": datetime.datetime.now().isoformat()
        }

        suggestions_path = 'data/suggestions.json'
        if os.path.exists(suggestions_path):
            with open(suggestions_path, 'r') as f:
                suggestions = json.load(f)
        else:
            suggestions = []

        suggestions.append(suggestion_entry)

        with open(suggestions_path, 'w') as f:
            json.dump(suggestions, f, indent=4)

        return render_template('index.html', feedback_message="Thanks for your suggestion!")
    except Exception as e:
        return render_template('index.html', feedback_message=f"Error: {str(e)}")


@app.route('/update_request', methods=['POST'])
def update_request():
    try:
        action = request.form['action']
        question = request.form['question']
        comment = request.form.get('comment', '')  # Supervisor comment

        if action == 'approve':
            final_answer = comment if comment.strip() else request.form['ai_suggestion']
            add_to_knowledge_base(question, final_answer)
            resolve_request(question, final_answer, comment)
            print(f"Follow-up: Approved answer for '{question}' sent to caller.")
        elif action == 'reject':
            resolve_request(question, None, comment)
            print(f"Follow-up: Request '{question}' was rejected.")

        return redirect('/requests')
    except Exception as e:
        return f"Error updating request: {str(e)}", 500

@app.route('/resolved')
def view_resolved():
    try:
        resolved_path = "data/resolved_requests.json"
        if os.path.exists(resolved_path):
            with open(resolved_path, "r") as file:
                resolved = json.load(file)
        else:
            resolved = []
        return render_template('resolved_requests.html', resolved=resolved)
    except Exception as e:
        return f"Error loading resolved requests: {str(e)}", 500

@app.route('/delete_resolved', methods=['POST'])
def delete_resolved():
    try:
        question_to_delete = request.form['question']
        resolved_path = "data/resolved_requests.json"

        if os.path.exists(resolved_path):
            with open(resolved_path, "r") as file:
                resolved = json.load(file)
        else:
            resolved = []

        resolved = [item for item in resolved if item["question"] != question_to_delete]

        with open(resolved_path, "w") as file:
            json.dump(resolved, file, indent=4)

        return redirect('/resolved')
    except Exception as e:
        return f"Error deleting resolved request: {str(e)}", 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        feedback_type = request.form.get('feedback')  # 'upvote' or 'downvote'
        question = request.form.get('question')
        answer = request.form.get('answer')

        feedback_entry = {
            "question": question,
            "answer": answer,
            "feedback": feedback_type,
            "timestamp": datetime.datetime.now().isoformat()
        }

        feedback_path = 'data/feedback.json'
        if os.path.exists(feedback_path):
            with open(feedback_path, 'r') as f:
                data = json.load(f)
        else:
            data = []

        data.append(feedback_entry)

        with open(feedback_path, 'w') as f:
            json.dump(data, f, indent=4)

        if feedback_type == "upvote":
            feedback_message = "Thanks! We're glad it helped!"
        else:
            feedback_message = "Sorry! We'll improve it next time."

        return render_template('index.html', question=question, answer=answer,
                               feedback_submitted=True, feedback_type=feedback_type,
                               feedback_message=feedback_message)
    except Exception as e:
        return render_template('index.html', feedback_message=f"Feedback error: {str(e)}")

# This will store simulated help queries


@app.route('/simulate-livekit', methods=['POST'])
def simulate_livekit():
    from flask import request, jsonify
    import datetime

    data = request.get_json()
    query = data.get('query', '')

    # Add to help requests like any unanswered user query
    from help_requests import add_help_request
    add_help_request(query, source="LiveKit")

    print("Simulated LiveKit request logged:", query)

    return jsonify({'status': 'success', 'message': 'Logged LiveKit request'}), 200

@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions_page():
    suggestions_file = 'data/suggestions.json'

    # Load suggestions
    if os.path.exists(suggestions_file):
        with open(suggestions_file) as f:
            suggestions = json.load(f)
    else:
        suggestions = []

    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        suggestion_text = request.form['suggestion']

        new_suggestion = {
            'question': question,
            'answer': answer,
            'suggestion': suggestion_text
        }

        suggestions.append(new_suggestion)

        with open(suggestions_file, 'w') as f:
            json.dump(suggestions, f, indent=4)

        # Save message to session and redirect (PRG)
        return redirect(url_for('suggestions_page', submitted='true'))

    # Handle message via query param
    message = "✅ Suggestion submitted!" if request.args.get('submitted') else None

    return render_template('suggestions.html', suggestions=suggestions, message=message)

if __name__ == '__main__':
    app.run(debug=True)
