from textblob import TextBlob
from jira import JIRA
from dotenv import load_dotenv
import os

# --------- LOAD ENV ---------
load_dotenv()

JIRA_SERVER = os.getenv('JIRA_SERVER')
JIRA_USER = os.getenv('JIRA_USER')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY')
JIRA_ISSUE_TYPE = os.getenv('JIRA_ISSUE_TYPE')
LOG_FILE = 'logs.txt'

# --------- FUNCTIONS ---------

def classify_log(log):
    blob = TextBlob(log)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "POSITIVE", polarity
    elif polarity < -0.1:
        return "NEGATIVE", polarity
    else:
        return "NEUTRAL", polarity

def simple_summarize(logs, top_n=5):
    sorted_logs = sorted(logs, key=lambda x: abs(x[2]), reverse=True)
    summary_lines = [f"{label}: {log}" for log, label, score in sorted_logs[:top_n]]
    return "\n".join(summary_lines)

def create_jira_ticket(summary):
    options = {'server': JIRA_SERVER}
    jira = JIRA(options, basic_auth=(JIRA_USER, JIRA_API_TOKEN))
    issue_dict = {
        'project': {'key': JIRA_PROJECT_KEY},
        'summary': 'Automated Log Analysis - Critical Logs Detected',
        'description': summary,
        'issuetype': {'name': JIRA_ISSUE_TYPE},
    }
    new_issue = jira.create_issue(fields=issue_dict)
    return new_issue.key

# --------- MAIN ---------

with open(LOG_FILE, 'r') as f:
    logs = [line.strip() for line in f if line.strip()]

classified_logs = []
for log in logs:
    label, score = classify_log(log)
    classified_logs.append((log, label, score))

summary = simple_summarize(classified_logs)
print("Summary:\n", summary)

# Only NEGATIVE logs go to Jira
critical_logs = [ (log, label, score) for (log, label, score) in classified_logs if label == 'NEGATIVE' ]

if critical_logs:
    jira_summary = simple_summarize(critical_logs, top_n=10)
    ticket_id = create_jira_ticket(jira_summary)
    print(f"Created Jira ticket: {ticket_id}")
else:
    print("No critical logs to create Jira ticket.")
