# Human-in-the-Loop AI Supervisor

## 📌 Overview

This is a locally running system simulating an AI receptionist for a fictional salon. When the AI cannot confidently answer a query, it escalates the question to a human supervisor, stores the resolution, and uses it to learn for the future.

## ✅ Features Implemented

- Supervisor UI to view and respond to unresolved help requests.
- Knowledge base to display learned answers, editable through the UI.
- Request lifecycle: creation → pending → resolved.
- JSON-based local storage for persistent request and KB data.
- Modular Flask application using separate logic files for clarity.

## 🚧 Pending Features

- LiveKit call simulation (to simulate AI answering phone calls).
- Console-based simulation/log of AI call reception and escalation.
- Simulated notification ("texting") to supervisor when help is needed.
- Follow-up message simulation to the customer after supervisor replies.
- Timeout logic to auto-mark requests unresolved after a delay.
- More robust KB update integration directly linked to resolved requests.

## 📂 Project Structure

├── app.py # Main Flask app controller
├── ai_agent.py # Logic for answering queries and escalating
├── help_requests.py # Request lifecycle management and data ops
├── data/
│ ├── help_requests.json # Stores all help request data
│ └── knowledge_base.json # Stores the knowledge base
├── templates/
│ ├── index.html # Homepage (AI agent interface)
│ ├── requests.html # Supervisor's request dashboard
│ └── kb.html # Knowledge base viewer/editor
├── static/ (optional) # For custom CSS or JS if added
└── requirements.txt # Python dependencies


## 💻 How to Run

Make sure Python and pip are installed. Then:

```bash
pip install -r requirements.txt
python app.py

# 1.Clear Lifecycle for Requests
# There's no timeout mechanism to mark requests as "Unresolved" if a supervisor doesn’t respond.
# Request status should clearly change: Pending → Resolved / Unresolved.

# 2.Follow-Up to Customer
# When a supervisor responds, there's no simulation of the AI following up with the original customer.
# A simple console log simulating "texting back" would suffice.

# 3.Updating Knowledge Base
# There is no visible mechanism where supervisor answers are saved and then reused by the AI in future interactions.
# You need to integrate supervisor responses into the KB dynamically.

# 4.Learned Answers UI
# No separate view or section for “Learned Answers” (from supervisor responses) exists.
# Add a route to display what the AI has learned over time.

