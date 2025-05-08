import json
import os
import datetime

PENDING_PATH = 'data/help_requests.json'
RESOLVED_PATH = 'data/resolved_requests.json'
TIMEOUT_MINUTES = 10  # set timeout here

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as file:
            return json.load(file)
    return []

def save_json(path, data):
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)

def mark_unresolved_requests():
    now = datetime.datetime.now()
    pending = load_json(PENDING_PATH)
    resolved = load_json(RESOLVED_PATH)
    still_pending = []

    for request in pending:
        if 'timestamp' not in request:
            print(f"[Warning] Skipped request with no timestamp: {request.get('question', 'Unknown')}")
            still_pending.append(request)
            continue

        try:
            timestamp = datetime.datetime.fromisoformat(request['timestamp'])
            age_minutes = (now - timestamp).total_seconds() / 60.0

            if age_minutes > TIMEOUT_MINUTES:
                unresolved_entry = {
                    "question": request['question'],
                    "answer": None,
                    "ai_suggestion": request.get('ai_suggestion', None),
                    "supervisor_comment": "Marked unresolved due to timeout",
                    "status": "unresolved",
                    "timestamp": timestamp.isoformat(),
                    "resolved_at": now.isoformat()
                }
                resolved.append(unresolved_entry)
                print(f"[Timeout] Marked as unresolved: {request['question']}")
            else:
                still_pending.append(request)

        except Exception as e:
            print(f"[Error] Failed to parse timestamp: {e}")
            still_pending.append(request)

    save_json(PENDING_PATH, still_pending)
    save_json(RESOLVED_PATH, resolved)


if __name__ == "__main__":
    mark_unresolved_requests()
