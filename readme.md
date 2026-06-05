# Smart_email_assistant

A Python-based Smart Email Assistant Agent that analyzes emails using rule-based logic.  
It can classify emails, detect priority, check sentiment and tone, extract deadlines, suggest replies, and save email history locally.

## Project Overview

The **smart_email_assistant** is a beginner-friendly Python project designed to help users manage emails more effectively.  
The user enters an email subject and body, and the system analyzes the email using keyword-based rules.

This project does not use any paid API or external AI model. It runs locally using Python.

## Real-World Problem

Students and workers receive many emails every day. Some emails are urgent, some are academic, some are meeting-related, and some may be spam or promotional messages.

Because of too many emails, important messages can be missed. This project helps by quickly identifying the email type, priority, sentiment, deadline, and possible reply.


## Agent Flow: Observe, Think, Act

This project follows an agent-style workflow:

### 1. Observe

The system observes the email by reading the subject and body.  
It preprocesses the text and identifies useful information such as keywords, dates, names, and email addresses.

### 2. Think

The system thinks using a rule-based analysis engine.  
It classifies the email category, detects priority, checks sentiment and tone, extracts deadlines and action items, and calculates a confidence score.

### 3. Act

The system acts by generating a summary, suggesting replies, answering follow-up questions, and saving the result in a JSON history file.

## Features

- Email category classification
- Priority detection
- Sentiment analysis
- Tone detection
- Deadline extraction
- Action item extraction
- Named entity detection
- One-sentence email summary
- Suggested replies
- Follow-up question answering
- Email history viewer
- Inbox statistics dashboard
- JSON logging

## Email Categories

The system can classify emails into categories such as:

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
- Rule-based logic
- Keyword matching
- Rich library for terminal display

## How to Run the Project

First, install the required library:

```bash
pip install rich
```

Then run the Python file:

```bash
python3 smart_email_assistant.py
```

## Project Files

```text
smart-email-assistant-agent/
│
├── smart_email_assistant.py
├── readme.md

```

## Example Input

```text
Subject: Assignment 3 due next Friday

Body:
Dear students, please remember that Assignment 3 is due next Friday.
Please review the chapters before submission.
```

## Example Output

```text
Category: Assignment/Study
Priority: Medium
Sentiment: Neutral
Tone: Formal
Deadline: next Friday
Suggested Reply: Thank you for the reminder. I will complete and submit it on time.
```

## Why This Project Is Useful

This project is useful because it saves time and helps users understand emails faster.  
Instead of reading every email carefully, the assistant gives a quick analysis and suggested action.

It can be helpful for students, office workers, and anyone who receives many emails daily.

## Author

Arbin Bhattarai