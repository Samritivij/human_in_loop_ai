import json
import os

KB_FILE = 'data/knowledge_base.json'

def load_knowledge_base():
    if not os.path.exists(KB_FILE):
        return []
    with open(KB_FILE, 'r') as f:
        return json.load(f)
    
def save_knowledge_base(kb):
    with open(KB_FILE, 'w') as f:
        json.dump(kb, f, indent=4)

def get_answer_from_kb(question):
    kb = load_knowledge_base()
    for entry in kb:
        if entry['question'].lower().strip() == question.lower().strip():
            answer = entry['answer']
            return answer if answer.lower() != 'none' else None
    return None

def add_to_knowledge_base(question, answer):
    kb = load_knowledge_base()
    kb.append({"question": question, "answer": answer})
    with open(KB_FILE, 'w') as f:
        json.dump(kb, f, indent=4)

def generate_response(question):
    if not os.path.exists(KB_FILE):
        return None

    with open(KB_FILE, 'r') as f:
        kb = json.load(f)

    for entry in kb:
        if entry['question'].lower().strip() == question.lower().strip():
            answer = entry['answer']
            if answer and answer.lower() != 'none':
                return answer
            else:
                return None  # No valid AI suggestion found

    return None  # Not found in knowledge base
