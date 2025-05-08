import json
from ai_agent import generate_response
import os
from datetime import datetime
from datetime import timedelta

REQUEST_TIMEOUT_MINUTES = 10  # or whatever you want

HELP_REQUESTS_FILE = 'data/help_requests.json'
RESOLVED_REQUESTS_FILE = 'data/resolved_requests.json'

KNOWLEDGE_BASE_FILE = 'data/knowledge_base.json'

def generate_response(question):
    if not os.path.exists(KNOWLEDGE_BASE_FILE):
        return None

    with open(KNOWLEDGE_BASE_FILE, 'r') as f:
        kb = json.load(f)

    for entry in kb:
        if entry['question'].lower().strip() == question.lower().strip():
            answer = entry['answer']
            if answer and answer.lower() != 'none':
                return answer
            else:
                return None  # No valid AI suggestion found

    return None  # Not found in knowledge base

def load_requests():
    if not os.path.exists(HELP_REQUESTS_FILE):
        return []
    with open(HELP_REQUESTS_FILE, 'r') as f:
        return json.load(f)

def save_requests(requests):
    with open(HELP_REQUESTS_FILE, 'w') as f:
        json.dump(requests, f, indent=4)

def add_to_knowledge_base(question, answer):
    # Ensure knowledge_base.json exists
    if not os.path.exists(KNOWLEDGE_BASE_FILE):
        with open(KNOWLEDGE_BASE_FILE, "w") as f:
            json.dump([], f)

    with open(KNOWLEDGE_BASE_FILE, "r") as f:
        kb = json.load(f)

    # Avoid duplicate questions
    for item in kb:
        if item["question"].strip().lower() == question.strip().lower():
            return

    kb.append({
        "question": question,
        "answer": answer
    })

    with open(KNOWLEDGE_BASE_FILE, "w") as f:
        json.dump(kb, f, indent=4)


def get_all_requests():
    requests = load_requests()
    return [r for r in requests if not r.get("resolved", False)]

def add_help_request(question, ai_suggestion=None, source="User"):
    requests = load_requests()
    new_id = max([r.get("id", 0) for r in requests], default=0) + 1

    if ai_suggestion is None:
        ai_suggestion = generate_response(question)

    new_request = {
    "id": new_id,
    "question": question,
    "ai_suggestion": ai_suggestion,
    "resolved": False,
    "timestamp": datetime.now().isoformat(),
    "status": "pending",  # 👈 Add status
    "source": source
}

    requests.append(new_request)
    save_requests(requests)


def mark_request_resolved(question):
    requests = load_requests()
    for r in requests:
        if r['question'] == question:
            r['resolved'] = True
    save_requests(requests)

def mark_timeouts_as_unresolved():
    now = datetime.now()
    changed = False
    requests = load_requests()

    for r in requests:
        if not r.get("resolved", False) and r.get("status") == "pending":
            created_time = datetime.fromisoformat(r["timestamp"])
            if now - created_time > timedelta(minutes=REQUEST_TIMEOUT_MINUTES):
                r["status"] = "unresolved"
                r["resolved"] = True  # Mark it resolved but failed
                changed = True

    if changed:
        save_requests(requests)
        
def resolve_request(question, ai_suggestion=None, comment=None):
    mark_request_resolved(question)
    unresolved = load_requests()

    if ai_suggestion is None:
        for r in unresolved:
            if r["question"] == question:
                ai_suggestion = r.get("ai_suggestion")
                break

    if os.path.exists(RESOLVED_REQUESTS_FILE):
        with open(RESOLVED_REQUESTS_FILE, 'r') as file:
            try:
                resolved = json.load(file)
            except json.JSONDecodeError:
                resolved = []
    else:
        resolved = []

    status = "approved" if ai_suggestion else "rejected"

    resolved.append({
        'question': question,
        'ai_suggestion': ai_suggestion,
        'supervisor_comment': comment,
        'resolved_at': datetime.now().isoformat(),
        'status': status
    })

    with open(RESOLVED_REQUESTS_FILE, 'w') as file:
        json.dump(resolved, file, indent=4)

    # ✅ Add the resolved answer to the knowledge base
    if ai_suggestion:  # Only add if there's a valid answer
        add_to_knowledge_base(question, ai_suggestion)
