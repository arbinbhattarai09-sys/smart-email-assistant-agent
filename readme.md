# Smart Email Assistant Agent

## Project Description

Smart Email Assistant Agent is a Python-based rule-based AI agent that helps users manage email overload. The user enters an email subject and body, and the agent analyzes the email to classify it, detect urgency, understand sentiment and tone, extract deadlines and action items, and suggest replies.

This project does not require any API key. It runs locally using Python keyword-based and rule-based logic.

## Real-World Problem

Students and workers receive many emails every day. Important emails from professors, classmates, or workplaces may get buried under promotions, newsletters, and spam messages. Reading every email manually takes time, and writing replies can also be difficult.

This project helps users quickly identify important emails and respond faster.

## Agent Model: Observe, Think, Act

### Observe
The agent reads the email subject and body and prepares the text for analysis.

### Think
The agent uses weighted keyword scoring and rule-based logic to classify the email. It also detects priority, sentiment, tone, deadlines, action items, and important entities.

### Act
The agent displays the result, suggests replies, answers follow-up questions, and saves email history locally.

## Features

- Email classification
- Confidence score
- Priority detection
- Sentiment detection
- Tone detection
- Deadline extraction
- Action item extraction
- Named entity detection
- Suggested reply generation
- Follow-up Q&A
- Email history viewer
- Inbox statistics dashboard
- JSON logging
- No API key required

## Email Categories

The agent classifies emails into these categories:

- Urgent
- Assignment/Study
- Meeting
- Promotion
- Spam
- Personal
- Reply Needed

## Technologies Used

- Python
- Regular Expressions
- JSON
- Rich library for better terminal output

## How to Run

Install Rich for better terminal output:

```bash
python3 -m pip install rich

## Example Use Case

 student receives an email from a professor about an assignment deadline. The agent reads the subject and body, classifies it as Assignment/Study or Urgent, detects the priority, finds the deadline, and suggests a reply.

Future Improvement

In the future, this project can be connected to Gmail API so that:

Spam emails can be moved to the spam folder
High-priority emails can be labeled and saved as drafts
Low-priority emails can be labeled for later review

Author
Arbin Bhattarai
