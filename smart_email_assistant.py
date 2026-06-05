"""
╔══════════════════════════════════════════════════════════╗
║                    smart_email_assistant                ║
╚══════════════════════════════════════════════════════════╝

"""
import re
import json
import os
import time
import random
from datetime import datetime
from collections import Counter, defaultdict

# ── Rich ──────────────────────────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.prompt import Prompt
    from rich.progress import track
    from rich import box
    RICH = True
    console = Console()
except ImportError:
    RICH = False

# ══════════════════════════════════════════════════════════════════════════════
#  KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════════════════

CATEGORIES = {
    "Urgent": {
        "icon": "🚨", "color": "bold red",
        "keywords": {
            "urgent": 4, "asap": 4, "immediately": 3, "critical": 4,
            "emergency": 4, "right away": 3, "deadline": 3, "overdue": 3,
            "final warning": 4, "last chance": 3, "action required": 3,
            "must respond": 3, "time sensitive": 3, "by tonight": 3,
            "by tomorrow": 2, "lose your marks": 4, "fail": 2,
            "escalate": 3, "do not ignore": 3, "respond now": 4,
        },
    },
    "Assignment/Study": {
        "icon": "📚", "color": "bold green",
        "keywords": {
            "assignment": 3, "homework": 3, "due": 2, "submit": 2,
            "submission": 3, "exam": 3, "quiz": 3, "lecture": 2,
            "study": 2, "course": 2, "class": 1, "professor": 2,
            "grades": 2, "grade": 2, "marks": 2, "tutorial": 2,
            "semester": 2, "project": 2, "report": 2, "essay": 3,
            "thesis": 3, "dissertation": 3, "lab": 2, "chapter": 2,
            "textbook": 2, "research": 2, "presentation": 2, "group work": 2,
        },
    },
    "Meeting": {
        "icon": "📅", "color": "bold blue",
        "keywords": {
            "meeting": 4, "schedule": 3, "zoom": 3, "call": 2,
            "calendar": 3, "invite": 3, "agenda": 3, "conference": 3,
            "teams": 2, "webinar": 3, "appointment": 3, "catch up": 2,
            "sync": 2, "standup": 3, "interview": 3, "rsvp": 4,
            "availability": 3, "book a time": 3, "let's meet": 3,
            "discussion": 2, "session": 2, "talk": 1,
        },
    },
    "Promotion": {
        "icon": "🛒", "color": "bold yellow",
        "keywords": {
            "sale": 3, "discount": 3, "offer": 2, "promo": 3,
            "coupon": 3, "deal": 2, "off": 1, "limited time": 3,
            "shop": 2, "buy": 2, "order": 1, "subscribe": 2,
            "newsletter": 3, "exclusive": 2, "savings": 2, "free shipping": 3,
            "flash sale": 4, "clearance": 3, "new arrivals": 2, "checkout": 2,
            "unsubscribe": 2, "marketing": 2, "promotional": 3,
        },
    },
    "Spam": {
        "icon": "🚫", "color": "bold magenta",
        "keywords": {
            "winner": 4, "won": 3, "prize": 4, "lottery": 4,
            "claim": 3, "free gift": 4, "congratulations": 2,
            "selected": 2, "click here": 3, "verify account": 4,
            "password": 3, "bank": 2, "suspicious": 3, "unusual activity": 4,
            "act now": 3, "expires": 2, "bitcoin": 3, "crypto": 2,
            "investment opportunity": 4, "nigerian": 4, "prince": 3,
            "transfer": 2, "million dollars": 4, "inheritance": 4,
        },
    },
    "Personal": {
        "icon": "👋", "color": "bold cyan",
        "keywords": {
            "hey": 2, "hi there": 2, "long time": 3, "miss you": 3,
            "catch up": 2, "coffee": 2, "hangout": 3, "friend": 2,
            "family": 2, "birthday": 3, "party": 2, "weekend": 2,
            "vacation": 2, "holiday": 2, "how are you": 3, "hope you": 2,
            "dinner": 2, "lunch": 2, "personal": 2, "gossip": 2,
            "fun": 1, "exciting news": 2, "big news": 2,
        },
    },
    "Reply Needed": {
        "icon": "↩️", "color": "bold white",
        "keywords": {
            "please reply": 4, "let me know": 3, "your thoughts": 3,
            "can you": 3, "could you": 3, "would you": 3,
            "please respond": 4, "awaiting": 3, "waiting for": 3,
            "feedback": 3, "review": 2, "opinion": 2, "confirm": 3,
            "confirmation": 3, "get back to me": 4, "respond": 3,
            "reply": 3, "what do you think": 4, "do you agree": 3,
            "are you available": 3, "can we": 2,
        },
    },
}

PRIORITY_SIGNALS = {
    "Critical": ["emergency", "critical", "system down", "data loss",
                 "immediately", "asap", "urgent", "right now", "on fire",
                 "lose your marks", "final warning", "last chance"],
    "High":     ["important", "priority", "soon", "today", "by tonight",
                 "overdue", "deadline", "must", "required", "action needed"],
    "Medium":   ["please", "when you can", "next week", "by friday",
                 "reminder", "follow up", "check in", "update"],
    "Low":      ["fyi", "no rush", "whenever", "just wanted", "heads up",
                 "newsletter", "digest", "monthly"],
}

SENTIMENT_SIGNALS = {
    "Positive": ["thanks", "thank you", "great", "excellent", "wonderful",
                 "amazing", "appreciate", "happy", "glad", "pleased",
                 "good news", "congratulations", "well done", "fantastic",
                 "love", "excited", "looking forward", "best", "awesome"],
    "Negative": ["sorry", "apologize", "problem", "issue", "error",
                 "wrong", "failed", "unfortunately", "disappointed",
                 "complaint", "concern", "trouble", "urgent", "angry",
                 "frustrated", "unacceptable", "poor", "bad", "terrible"],
}

TONE_SIGNALS = {
    "Formal":      ["dear", "sincerely", "regards", "hereby", "pursuant",
                    "kindly", "respectfully", "please find", "attached"],
    "Informal":    ["hey", "hi", "sup", "lol", "haha", "cool", "awesome",
                    "btw", "fyi", "gonna", "wanna", "tbh"],
    "Aggressive":  ["immediately", "demand", "unacceptable", "warning",
                    "must", "final notice", "do not ignore", "failure"],
    "Friendly":    ["hope you", "how are you", "miss you", "catch up",
                    "excited", "looking forward", "take care", "cheers"],
    "Professional":["team", "project", "deliverable", "milestone", "kpi",
                    "stakeholder", "agenda", "action items", "follow up"],
}

# Deadline patterns
DEADLINE_PATTERNS = [
    r'\b(by|before|due|deadline[:\s]+|submit\s+by)\s+([\w\s,]+\d{4})',
    r'\b(tonight|tomorrow|today)\b',
    r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
    r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?'
    r'|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?'
    r'|dec(?:ember)?)\s+\d{1,2}(?:\s*,?\s*\d{4})?\b',
    r'\b\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?\b',
    r'\b\d{1,2}:\d{2}\s*(?:am|pm)\b',
    r'\bnext\s+(week|month|monday|tuesday|wednesday|thursday|friday)\b',
]

# Action item patterns
ACTION_PATTERNS = [
    r'(?:please|kindly|could you|can you|you must|you need to|make sure to|remember to|don\'t forget to)\s+([^.!?\n]{5,60})',
    r'(?:submit|send|review|complete|finish|respond to|reply to|confirm|attend|join|read|check)\s+([^.!?\n]{5,50})',
]

# Named entity patterns (simple heuristic)
ENTITY_PATTERNS = {
    "Person":  r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
    "Email":   r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b',
    "URL":     r'https?://[^\s]+',
    "Phone":   r'\b(?:\+?\d[\d\s\-()]{7,14}\d)\b',
    "Time":    r'\b\d{1,2}:\d{2}\s*(?:[AP]M)?\b',
    "Date":    r'\b\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?\b',
}

# Reply templates per category and tone
REPLY_TEMPLATES = {
    "Urgent": {
        "Formal":  "Dear {sender},\n\nThank you for bringing this to my attention. I understand the urgency and will address this matter immediately.\n\nBest regards,\n{name}",
        "Casual":  "Got it! I'll take care of this right away. Thanks for the heads up.",
        "Brief":   "Understood — on it immediately.",
    },
    "Assignment/Study": {
        "Formal":  "Dear {sender},\n\nThank you for the reminder regarding {subject_hint}. I have noted the requirements and will ensure timely submission.\n\nBest regards,\n{name}",
        "Casual":  "Thanks for the heads up! I'll make sure to get it done on time.",
        "Brief":   "Got it, thanks! Will submit on time.",
    },
    "Meeting": {
        "Formal":  "Dear {sender},\n\nThank you for the meeting invitation. I confirm my availability and will attend as scheduled. Please share any agenda items in advance.\n\nBest regards,\n{name}",
        "Casual":  "Sounds good! I'll be there. See you then!",
        "Brief":   "Confirmed — I'll attend.",
    },
    "Promotion": {
        "Formal":  "Thank you for your promotional message. I will review the offer and follow up if interested.",
        "Casual":  "Thanks! I'll check it out when I get a chance.",
        "Brief":   "Thanks, noted.",
    },
    "Spam": {
        "Formal":  "This message appears to be unsolicited. I have flagged it appropriately.",
        "Casual":  "This looks like spam — ignoring.",
        "Brief":   "Marked as spam.",
    },
    "Personal": {
        "Formal":  "Dear {sender},\n\nThank you for reaching out. It was wonderful to hear from you. I look forward to catching up soon.\n\nWarm regards,\n{name}",
        "Casual":  "Hey! So great to hear from you! Let's definitely catch up soon 😊",
        "Brief":   "Great to hear from you! Let's catch up soon!",
    },
    "Reply Needed": {
        "Formal":  "Dear {sender},\n\nThank you for your message. I have reviewed your request and will provide a detailed response shortly.\n\nBest regards,\n{name}",
        "Casual":  "Hey! Thanks for reaching out. I'll get back to you with my thoughts soon!",
        "Brief":   "Thanks! I'll get back to you shortly.",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
#  CORE ANALYSIS ENGINE


TIE_BREAK_ORDER = [
    "Urgent", "Assignment/Study", "Meeting",
    "Reply Needed", "Personal", "Promotion", "Spam"
]


def normalize(text: str) -> str:
    return text.lower()


def score_categories(text: str) -> dict:
    scores = defaultdict(float)
    for cat, data in CATEGORIES.items():
        for kw, weight in data["keywords"].items():
            count = len(re.findall(r'\b' + re.escape(kw) + r'\b', text))
            scores[cat] += count * weight
    return dict(scores)


def pick_category(scores: dict) -> tuple:
    if not any(scores.values()):
        return "Reply Needed", 0.0

    max_score = max(scores.values())
    top_cats  = [c for c, s in scores.items() if s == max_score]

    # Tie-break by priority order
    winner = sorted(top_cats, key=lambda c: TIE_BREAK_ORDER.index(c))[0]

    total = sum(scores.values())
    confidence = round((max_score / total * 100) if total > 0 else 0, 1)
    return winner, confidence


def detect_priority(text: str) -> str:
    for level in ["Critical", "High", "Medium", "Low"]:
        for kw in PRIORITY_SIGNALS[level]:
            if kw in text:
                return level
    return "Low"


def detect_sentiment(text: str) -> str:
    pos = sum(1 for w in SENTIMENT_SIGNALS["Positive"] if w in text)
    neg = sum(1 for w in SENTIMENT_SIGNALS["Negative"] if w in text)
    if pos > neg:   return "Positive"
    elif neg > pos: return "Negative"
    return "Neutral"


def detect_tone(text: str) -> str:
    tone_scores = {t: 0 for t in TONE_SIGNALS}
    for tone, signals in TONE_SIGNALS.items():
        for s in signals:
            if s in text:
                tone_scores[tone] += 1
    return max(tone_scores, key=tone_scores.get)


def extract_deadlines(text: str) -> list:
    found = []
    for pattern in DEADLINE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            d = m if isinstance(m, str) else " ".join(m).strip()
            if d and d not in found:
                found.append(d)
    return found[:3]  # return up to 3


def extract_action_items(text: str) -> list:
    items = []
    for pattern in ACTION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            item = m.strip().rstrip(".,;:")
            if len(item) > 5 and item not in items:
                items.append(item.capitalize())
    return items[:5]


def extract_entities(text: str) -> dict:
    found = defaultdict(list)
    for entity_type, pattern in ENTITY_PATTERNS.items():
        matches = re.findall(pattern, text)
        for m in matches:
            if m not in found[entity_type]:
                found[entity_type].append(m)
    return dict(found)


def get_matched_keywords(text: str, category: str) -> list:
    kws = []
    for kw in CATEGORIES[category]["keywords"]:
        if re.search(r'\b' + re.escape(kw) + r'\b', text):
            kws.append(kw)
    return kws[:8]


def generate_summary(subject: str, category: str, priority: str, sentiment: str,
                     deadlines: list, action_items: list) -> str:
    """Build a one-sentence summary without any AI."""
    parts = []

    cat_phrases = {
        "Urgent":           "an urgent message requiring immediate attention",
        "Assignment/Study": "an academic email about coursework or assignments",
        "Meeting":          "a meeting-related email about scheduling",
        "Promotion":        "a promotional or marketing email",
        "Spam":             "a suspicious or junk email",
        "Personal":         "a personal message from someone you know",
        "Reply Needed":     "an email that requires your response",
    }

    summary = f"This is {cat_phrases.get(category, 'an email')}"

    if deadlines:
        summary += f", with a deadline of {deadlines[0]}"
    if action_items:
        summary += f"; main action: {action_items[0].lower()}"
    if priority in ("Critical", "High"):
        summary += f" — marked {priority.lower()} priority"

    return summary + "."


def build_replies(category: str, subject: str) -> dict:
    """Build context-aware replies by filling in template variables."""
    templates = REPLY_TEMPLATES.get(category, REPLY_TEMPLATES["Reply Needed"])

    # Extract a short subject hint
    hint = subject[:40].strip()

    replies = {}
    for tone, template in templates.items():
        reply = template.replace("{sender}", "Professor / Team")
        reply = reply.replace("{name}", "Arbin")
        reply = reply.replace("{subject_hint}", hint)
        replies[tone] = reply
    return replies


def analyze_email(subject: str, body: str) -> dict:
    """Master analysis function — returns full result dict."""
    combined = normalize(subject + " " + body)

    # Core signals
    scores     = score_categories(combined)
    category, confidence = pick_category(scores)
    priority   = detect_priority(combined)
    sentiment  = detect_sentiment(combined)
    tone       = detect_tone(combined)

    # Extraction
    deadlines    = extract_deadlines(combined)
    action_items = extract_action_items(body)
    entities     = extract_entities(subject + " " + body)
    keywords     = get_matched_keywords(combined, category)

    # Summary & replies
    summary = generate_summary(subject, category, priority, sentiment,
                               deadlines, action_items)
    replies = build_replies(category, subject)

    return {
        "category":     category,
        "confidence":   confidence,
        "priority":     priority,
        "sentiment":    sentiment,
        "tone":         tone,
        "summary":      summary,
        "deadlines":    deadlines,
        "action_items": action_items,
        "entities":     entities,
        "keywords":     keywords,
        "replies":      replies,
        "scores":       scores,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  RULE-BASED FOLLOW-UP Q&A


def answer_followup(question: str, result: dict, subject: str, body: str) -> str:
    """Answer follow-up questions about the analyzed email using rules."""
    q = question.lower()

    if any(w in q for w in ["category", "type", "kind"]):
        cat = result["category"]
        return (f"This email is classified as '{cat}' "
                f"({CATEGORIES[cat]['icon']}) with {result['confidence']}% confidence. "
                f"It matched keywords: {', '.join(result['keywords'][:5])}.")

    if any(w in q for w in ["priority", "urgent", "important"]):
        p = result["priority"]
        colors = {"Critical": "extremely urgent", "High": "quite important",
                  "Medium": "moderately important", "Low": "low priority"}
        return f"The priority is {p} — this email is {colors.get(p, p)}."

    if any(w in q for w in ["reply", "respond", "response", "say"]):
        replies = result["replies"]
        tone = "Formal" if "formal" in q else "Casual" if "casual" in q else "Brief"
        return f"Here's a {tone.lower()} reply:\n\n{replies.get(tone, list(replies.values())[0])}"

    if any(w in q for w in ["deadline", "due", "when"]):
        d = result["deadlines"]
        if d:
            return f"Detected deadline(s): {', '.join(d)}"
        return "No specific deadline was detected in this email."

    if any(w in q for w in ["action", "task", "do", "todo"]):
        items = result["action_items"]
        if items:
            return "Action items found:\n" + "\n".join(f"  • {i}" for i in items)
        return "No specific action items were detected."

    if any(w in q for w in ["sentiment", "tone", "feeling", "mood"]):
        return (f"Sentiment: {result['sentiment']} | Tone: {result['tone']}. "
                f"The email appears to have a {result['tone'].lower()} writing style "
                f"with a {result['sentiment'].lower()} emotional tone.")

    if any(w in q for w in ["entity", "person", "who", "email address", "contact"]):
        e = result["entities"]
        if e:
            parts = []
            for k, v in e.items():
                parts.append(f"{k}: {', '.join(v)}")
            return "Detected entities:\n" + "\n".join(f"  • {p}" for p in parts)
        return "No named entities were detected in this email."

    if any(w in q for w in ["summary", "about", "what is"]):
        return f"Summary: {result['summary']}"

    if any(w in q for w in ["spam", "scam", "safe", "legit"]):
        spam_score = result["scores"].get("Spam", 0)
        if spam_score > 5:
            return "⚠️  This email has strong spam indicators. Treat it with caution."
        elif spam_score > 2:
            return "This email has some spam-like signals but is not definitively spam."
        return "✅  This email does not appear to be spam."

    if any(w in q for w in ["confidence", "sure", "certain", "accurate"]):
        c = result["confidence"]
        if c >= 70:
            return f"Confidence is high at {c}% — the classification is likely correct."
        elif c >= 40:
            return f"Confidence is moderate at {c}% — classification may not be perfect."
        return f"Confidence is low at {c}% — the email content is ambiguous."

    if any(w in q for w in ["score", "keyword", "match"]):
        scores = result["scores"]
        top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        lines = [f"  {cat}: {score:.0f} pts" for cat, score in top]
        return "Top category scores:\n" + "\n".join(lines)

    # Default
    return (f"I can answer questions about: category, priority, replies, deadlines, "
            f"action items, sentiment/tone, entities, summary, spam risk, confidence, "
            f"or keyword scores. What would you like to know?")


# ══════════════════════════════════════════════════════════════════════════════
#  DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

def display_banner():
    if not RICH:
        print("\n" + "═"*62)
        print("  📧  smart_email_assistant")
        print("═"*62 + "\n")
        return

    title = Text(justify="center")
    title.append("\n")
    title.append("  📧  smart_email_assistant  \n", style="bold cyan")

    grid = Table.grid(expand=True)
    grid.add_column(justify="center")
    grid.add_row(title)

    console.print(Panel(grid, border_style="cyan", padding=(0, 4)))
    console.print()


def _conf_bar(conf: float) -> Text:
    """Render a gradient confidence bar with label."""
    total   = 30
    filled  = int(conf / 100 * total)
    empty   = total - filled
    if conf >= 75:   bar_color = "bold green"
    elif conf >= 45: bar_color = "bold yellow"
    else:            bar_color = "bold red"
    t = Text()
    t.append("━" * filled, style=bar_color)
    t.append("─" * empty,  style="dim")
    t.append(f"  {conf:.1f}%", style=bar_color)
    return t


def _score_bars(scores: dict) -> str:
    """Mini horizontal bar chart for all category scores."""
    total = max(sum(scores.values()), 1)
    lines = []
    for cat, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        icon  = CATEGORIES[cat]["icon"]
        pct   = score / total * 100
        bar_w = int(pct / 5)
        bar   = "▓" * bar_w + "░" * (20 - bar_w)
        lines.append(f"  {icon} {cat:<18s} {bar}  {score:.0f}pts")
    return "\n".join(lines)


def _priority_badge(priority: str) -> Text:
    badges = {
        "Critical": ("🔴 CRITICAL", "bold white on red"),
        "High":     ("🟠 HIGH",     "bold black on orange1"),
        "Medium":   ("🟡 MEDIUM",   "bold black on yellow"),
        "Low":      ("🟢 LOW",      "bold black on green"),
    }
    label, style = badges.get(priority, (priority, "white"))
    return Text(f" {label} ", style=style)


def _sentiment_badge(sent: str) -> Text:
    badges = {
        "Positive": ("😊 Positive", "bold green"),
        "Neutral":  ("😐 Neutral",  "bold yellow"),
        "Negative": ("😟 Negative", "bold red"),
    }
    label, style = badges.get(sent, (sent, "white"))
    return Text(label, style=style)


def _keyword_tags(keywords: list) -> Text:
    """Render keywords as inline tags."""
    t = Text()
    colors = ["cyan", "magenta", "yellow", "green", "blue", "red"]
    for i, kw in enumerate(keywords):
        t.append(f" {kw} ", style=f"bold black on {colors[i % len(colors)]}")
        t.append(" ")
    return t


def display_result(result: dict):
    cat       = result["category"]
    conf      = result["confidence"]
    priority  = result["priority"]
    sent      = result["sentiment"]
    tone      = result["tone"]
    summary   = result["summary"]
    deadlines = result["deadlines"]
    actions   = result["action_items"]
    entities  = result["entities"]
    keywords  = result["keywords"]
    replies   = result["replies"]
    scores    = result["scores"]

    SENT_ICON = {"Positive": "😊", "Neutral": "😐", "Negative": "😟"}
    PRI_COL   = {"Critical": "bold red", "High": "bold orange1",
                 "Medium": "bold yellow", "Low": "bold green"}

    # ── Plain-text fallback ───────────────────────────────────────────────────
    if not RICH:
        bar = "█" * int(conf / 5) + "░" * (20 - int(conf / 5))
        print("\n" + "═"*60)
        print(f"  {CATEGORIES[cat]['icon']}  CATEGORY  : {cat}")
        print(f"  CONFIDENCE : [{bar}] {conf:.1f}%")
        print(f"  PRIORITY   : {priority}")
        print(f"  SENTIMENT  : {sent} {SENT_ICON.get(sent,'')}")
        print(f"  TONE       : {tone}")
        print(f"\n  SUMMARY:\n  {summary}")
        if deadlines:
            print(f"\n  ⏰ DEADLINES : {', '.join(deadlines)}")
        if actions:
            print("\n  ✅ ACTION ITEMS:")
            for a in actions: print(f"     • {a}")
        if entities:
            print("\n  🔍 ENTITIES:")
            for k, v in entities.items():
                print(f"     [{k}] {', '.join(v)}")
        if keywords:
            print(f"\n  🏷  KEYWORDS  : {', '.join(keywords)}")
        print("\n  📊 CATEGORY SCORES:")
        for c, s in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            b = "█" * int(s / max(scores.values()) * 15) if s else ""
            print(f"     {CATEGORIES[c]['icon']} {c:<20s} {b} {s:.0f}")
        print("\n" + "─"*60)
        print("  💬 SUGGESTED REPLIES")
        print("─"*60)
        for tone_label, text in replies.items():
            print(f"\n  ┌─ {tone_label.upper()} ─")
            for line in text.split("\n"):
                print(f"  │ {line}")
            print("  └─")
        print("═"*60)
        return

    # ── RICH display ──────────────────────────────────────────────────────────
    console.print()
    console.print(Rule(
        f"[bold cyan]  📊 EMAIL ANALYSIS RESULT  [/bold cyan]",
        style="cyan"
    ))
    console.print()

    # ── SECTION 1: Header card ────────────────────────────────────────────────
    cat_icon  = CATEGORIES[cat]["icon"]
    cat_col   = CATEGORIES[cat]["color"]

    header = Text()
    header.append(f"\n  {cat_icon}  ", style="bold")
    header.append(cat.upper(), style=f"{cat_col} underline")
    header.append("   ")
    header.append(_priority_badge(priority))
    header.append("   ")
    header.append(_sentiment_badge(sent))
    header.append(f"\n\n  ", style="")
    header.append("Tone: ", style="dim")
    header.append(tone, style="bold")
    header.append("\n")

    console.print(Panel(
        header,
        title="[bold]Classification[/bold]",
        border_style=CATEGORIES[cat]["color"].replace("bold ", ""),
        padding=(0, 2),
    ))

    # ── SECTION 2: Confidence + Score breakdown (side by side) ────────────────
    conf_text = Text()
    conf_text.append("\n  Confidence Score\n\n  ", style="dim")
    conf_text.append(_conf_bar(conf))
    conf_text.append("\n\n  ", style="")
    conf_text.append("Higher = more certain about category\n", style="dim italic")

    score_text = Text("\n" + _score_bars(scores) + "\n")

    console.print(Columns([
        Panel(conf_text,  title="[bold cyan]📈 Confidence[/bold cyan]",  border_style="cyan"),
        Panel(score_text, title="[bold magenta]🏆 All Category Scores[/bold magenta]", border_style="magenta"),
    ], expand=True))

    # ── SECTION 3: Summary ────────────────────────────────────────────────────
    console.print(Panel(
        f"\n  [italic]{summary}[/italic]\n",
        title="[bold green]📝 Email Summary[/bold green]",
        border_style="green",
    ))

    # ── SECTION 4: Keywords ───────────────────────────────────────────────────
    if keywords:
        kw_text = Text("\n  ")
        kw_text.append_text(_keyword_tags(keywords))
        kw_text.append("\n")
        console.print(Panel(
            kw_text,
            title="[bold yellow]🏷  Matched Keywords[/bold yellow]",
            border_style="yellow",
        ))

    # ── SECTION 5: Deadlines + Actions side by side ───────────────────────────
    left_parts  = []
    right_parts = []

    if deadlines:
        dl_text = Text()
        for d in deadlines:
            dl_text.append(f"\n  ⏰  {d.upper()}\n", style="bold red")
        left_parts.append(Panel(
            dl_text,
            title="[bold red]⏰ Deadlines Detected[/bold red]",
            border_style="red",
        ))

    if actions:
        ac_lines = Text()
        for i, a in enumerate(actions, 1):
            ac_lines.append(f"\n  {i}. ", style="bold green")
            ac_lines.append(a + "\n", style="white")
        right_parts.append(Panel(
            ac_lines,
            title="[bold green]✅ Action Items[/bold green]",
            border_style="green",
        ))

    if left_parts and right_parts:
        console.print(Columns(left_parts + right_parts, expand=True))
    elif left_parts:
        console.print(*left_parts)
    elif right_parts:
        console.print(*right_parts)

    # ── SECTION 6: Entities ───────────────────────────────────────────────────
    if entities:
        ent_tbl = Table(show_header=True, box=box.SIMPLE, border_style="blue",
                        header_style="bold blue", padding=(0, 2))
        ent_tbl.add_column("Type",  style="dim",  width=12)
        ent_tbl.add_column("Value", style="cyan")
        for k, v in entities.items():
            icon_map = {"Email": "📧", "URL": "🔗", "Phone": "📞",
                        "Time": "🕐", "Date": "📅", "Person": "👤"}
            ent_tbl.add_row(
                f"{icon_map.get(k, '•')} {k}",
                ", ".join(v)
            )
        console.print(Panel(
            ent_tbl,
            title="[bold blue]🔍 Detected Entities[/bold blue]",
            border_style="blue",
        ))

    # ── SECTION 7: Suggested replies ─────────────────────────────────────────
    console.print()
    console.print(Rule("[bold yellow]  💬 SUGGESTED REPLIES  [/bold yellow]", style="yellow"))
    console.print()

    reply_configs = {
        "Formal":  ("blue",    "👔", "Professional tone"),
        "Casual":  ("cyan",    "😊", "Friendly tone"),
        "Brief":   ("magenta", "⚡", "Quick one-liner"),
    }
    panels = []
    for tone_label, reply_text in replies.items():
        color, icon, desc = reply_configs.get(tone_label, ("white", "💬", ""))
        body = Text()
        body.append(f"\n{reply_text}\n\n", style="white")
        body.append(f"  {desc}", style=f"dim {color} italic")
        panels.append(Panel(
            body,
            title=f"[bold {color}]{icon}  {tone_label}[/bold {color}]",
            border_style=color,
        ))
    console.print(Columns(panels, equal=True, expand=True))
    console.print()


def display_history(history: list):
    if not history:
        _info("No history yet.")
        return

    if not RICH:
        print("\n--- Email History (Last 10) ---")
        for i, e in enumerate(history[-10:], 1):
            print(f"{i}. [{e['category']}] {e['subject'][:45]}  [{e['timestamp']}]")
        return

    tbl = Table(title="📂 Email History (Last 10)",
                box=box.SIMPLE_HEAVY, border_style="dim", show_lines=True)
    tbl.add_column("#",         width=3,  style="dim")
    tbl.add_column("Subject",   width=32)
    tbl.add_column("Category",  width=18)
    tbl.add_column("Priority",  width=10)
    tbl.add_column("Conf",      width=7)
    tbl.add_column("Date",      width=18, style="dim")

    PRI_COL = {"Critical": "bold red", "High": "bold orange1",
               "Medium": "bold yellow", "Low": "bold green"}

    for i, e in enumerate(history[-10:], 1):
        cat = e.get("category", "?")
        pri = e.get("priority", "?")
        conf = e.get("confidence", 0)
        conf_col = "green" if conf >= 70 else "yellow" if conf >= 40 else "red"
        icon = CATEGORIES.get(cat, {}).get("icon", "📧")
        col  = CATEGORIES.get(cat, {}).get("color", "white")
        tbl.add_row(
            str(i),
            e.get("subject", "")[:32],
            Text(f"{icon} {cat}", style=col),
            Text(pri, style=PRI_COL.get(pri, "white")),
            Text(f"{conf}%", style=conf_col),
            e.get("timestamp", ""),
        )
    console.print(tbl)


def display_stats(history: list):
    if not history:
        _info("No stats yet.")
        return

    cats  = Counter(e.get("category") for e in history)
    pris  = Counter(e.get("priority") for e in history)
    sents = Counter(e.get("sentiment") for e in history)
    avg_conf = sum(e.get("confidence", 0) for e in history) / len(history)

    if not RICH:
        print("\n--- Inbox Statistics ---")
        print("Categories:", dict(cats))
        print("Priorities:", dict(pris))
        print("Sentiments:", dict(sents))
        print(f"Total emails: {len(history)} | Avg confidence: {avg_conf:.1f}%")
        return

    tbl = Table(title="📊 Inbox Statistics",
                box=box.ROUNDED, border_style="cyan")
    tbl.add_column("Metric",    style="bold", width=12)
    tbl.add_column("Value",     width=22)
    tbl.add_column("Count",     justify="right", width=7)

    PRI_COL = {"Critical": "bold red", "High": "bold orange1",
               "Medium": "bold yellow", "Low": "bold green"}

    for cat, count in cats.most_common():
        icon = CATEGORIES.get(cat, {}).get("icon", "📧")
        col  = CATEGORIES.get(cat, {}).get("color", "white")
        tbl.add_row("Category", Text(f"{icon} {cat}", style=col), str(count))

    tbl.add_section()
    for pri, count in pris.most_common():
        tbl.add_row("Priority", Text(pri, style=PRI_COL.get(pri, "white")), str(count))

    tbl.add_section()
    SENT_ICON = {"Positive": "😊", "Neutral": "😐", "Negative": "😟"}
    for sent, count in sents.most_common():
        tbl.add_row("Sentiment", f"{SENT_ICON.get(sent,'')} {sent}", str(count))

    tbl.add_section()
    tbl.add_row("[bold]Total[/bold]",      f"{len(history)} emails",   "")
    tbl.add_row("[bold]Avg Confidence[/bold]", f"{avg_conf:.1f}%",     "")

    console.print(tbl)


# ══════════════════════════════════════════════════════════════════════════════
#  LOGGING / HISTORY
# ══════════════════════════════════════════════════════════════════════════════

LOG_FILE     = "email_agent_log.json"
HISTORY_FILE = "email_history.json"


def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_history(history: list):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def log_result(subject: str, body: str, result: dict) -> dict:
    entry = {
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "subject":      subject,
        "body_preview": body[:100],
        "category":     result["category"],
        "confidence":   result["confidence"],
        "priority":     result["priority"],
        "sentiment":    result["sentiment"],
        "tone":         result["tone"],
        "deadlines":    result["deadlines"],
        "action_items": result["action_items"],
    }
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE) as f:
                logs = json.load(f)
        except Exception:
            pass
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
    return entry


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _info(msg):
    if RICH: console.print(f"[dim]{msg}[/dim]")
    else: print(msg)

def _ok(msg):
    if RICH: console.print(f"[bold green]✓ {msg}[/bold green]")
    else: print(f"OK: {msg}")

def _err(msg):
    if RICH: console.print(f"[bold red]✗ {msg}[/bold red]")
    else: print(f"ERROR: {msg}")


SAMPLE_EMAILS = [
    ("URGENT – Submit your lab report ASAP!",
     "Hi everyone, this is critical. Please submit immediately or you will lose your marks. Deadline is tonight at 11:59 PM."),
    ("Assignment 3 due next Friday",
     "Dear students, please remember that Assignment 3 on data structures is due next Friday. Review chapters 5-7 before submission."),
    ("Team meeting invite – Friday 2 PM",
     "Hi Arbin, I'd like to schedule a Zoom call this Friday at 2 PM to discuss the project progress. Please confirm your availability."),
    ("50% OFF – Today only! Flash sale",
     "Don't miss out! Get 50% off all items in our store today only. Use promo code FLASH50 at checkout. Limited time offer!"),
    ("Congratulations! You have won a FREE gift!",
     "You have been selected as our lucky winner! Click here to claim your free prize. Act now before it expires!"),
    ("Hey, long time no talk!",
     "Hey Arbin! It's been a while since we last caught up. Hope everything is going well with your studies. Let's grab coffee soon!"),
    ("Can you review my draft?",
     "Hi, I've attached my essay draft. Could you please review it and let me know your thoughts? I'd appreciate feedback before submission."),
    ("Grade appeal – please respond",
     "Dear professor, I believe there was an error in my midterm grading. I scored 85% but received 70% on the portal. Could you please review this?"),
]


def show_menu() -> str:
    if RICH:
        console.print(Rule())
        tbl = Table(show_header=False, box=None, padding=(0, 2))
        tbl.add_column(style="bold cyan")
        tbl.add_column(style="dim")
        for i, (subj, _) in enumerate(SAMPLE_EMAILS, 1):
            tbl.add_row(f"[{i}]", subj)
        tbl.add_row("[c]", "Type your own custom email")
        tbl.add_row("[h]", "View email history")
        tbl.add_row("[s]", "View inbox statistics")
        tbl.add_row("[q]", "Quit")
        console.print(Panel(tbl, title="[bold]Commands[/bold]", border_style="dim"))
        return Prompt.ask("Choose")
    else:
        print("\n--- Menu ---")
        for i, (subj, _) in enumerate(SAMPLE_EMAILS, 1):
            print(f"  [{i}] {subj}")
        print("  [c] Custom email\n  [h] History\n  [s] Stats\n  [q] Quit")
        return input("Choose: ").strip().lower()


def get_custom_email() -> tuple:
    if RICH:
        console.print(Rule("[bold cyan]✉️  Enter Email[/bold cyan]"))
        subject = Prompt.ask("[bold]Subject[/bold]")
        console.print("[bold]Body[/bold] (press Enter twice to finish):")
    else:
        print("\n--- Enter Email ---")
        subject = input("Subject: ").strip()
        print("Body (press Enter twice to finish):")
    lines, blanks = [], 0
    while blanks < 1:
        line = input()
        if line == "": blanks += 1
        else: blanks = 0; lines.append(line)
    return subject, "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    display_banner()
    history = load_history()

    while True:
        choice = show_menu()

        if choice == "q":
            _ok("Goodbye! Your session has been saved.")
            break

        elif choice == "h":
            display_history(history)
            continue

        elif choice == "s":
            display_stats(history)
            continue

        elif choice == "c":
            subject, body = get_custom_email()

        elif choice.isdigit() and 1 <= int(choice) <= len(SAMPLE_EMAILS):
            subject, body = SAMPLE_EMAILS[int(choice) - 1]

        else:
            _err("Invalid choice.")
            continue

        # Show input
        if RICH:
            console.print(Panel(
                f"[bold]Subject:[/bold] {subject}\n\n[bold]Body:[/bold]\n{body}",
                title="[dim]INPUT EMAIL[/dim]", border_style="dim"
            ))
        else:
            print(f"\nSubject: {subject}\nBody:\n{body}")

        # Fake a small loading delay for UX
        _info("Analyzing email...")
        time.sleep(0.4)

        # Analyze
        result = analyze_email(subject, body)

        # Display
        display_result(result)

        # Log & save
        entry = log_result(subject, body, result)
        history.append(entry)
        save_history(history)
        _ok(f"Saved to {LOG_FILE}")

        # Follow-up Q&A
        if RICH:
            console.print(Rule("[dim]💬 Follow-up Q&A[/dim]"))
            console.print("[dim]Ask a question about this email, or press Enter to go back.[/dim]")
        else:
            print("\n[Follow-up] Ask a question or press Enter to skip.")

        while True:
            if RICH:
                q = Prompt.ask("[dim]Ask[/dim]", default="")
            else:
                q = input("Ask: ").strip()
            if not q:
                break
            answer = answer_followup(q, result, subject, body)
            if RICH:
                console.print(Panel(answer,
                                    title="[bold cyan]Answer[/bold cyan]",
                                    border_style="cyan"))
            else:
                print(f"\nAnswer: {answer}\n")


if __name__ == "__main__":
    main()
