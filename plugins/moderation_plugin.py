# plugins/moderation_plugin.py

def ai_moderate(text):
    """
    Placeholder for future AI moderation engine.
    You can integrate a real AI model here later.
    """
    flagged = False
    reason = None

    bad_words = ["spam", "scam", "fuck"]

    for w in bad_words:
        if w in text.lower():
            flagged = True
            reason = f"Contains prohibited word: {w}"
            break

    return flagged, reason
