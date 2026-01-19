import re
import os
import datetime

# Basic stop words for keyword extraction
_STOP_WORDS = set([
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "and", "or", "but", "if", "then", "else", "when", "where", "how", "why",
    "for", "at", "by", "of", "on", "in", "with", "to", "from", "up", "down",
    "out", "off", "over", "under", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will",
    "just", "don", "should", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain",
    "aren", "couldn", "didn", "doesn", "hadn", "hasn", "haven", "isn", "ma",
    "mightn", "mustn", "needn", "shan", "shouldn", "wasn", "weren", "won", "wouldn"
])

# Basic sentiment keywords (can be expanded)
_POSITIVE_KEYWORDS = set(["win", "success", "accomplished", "best", "great", "good", "happy", "positive", "awesome", "effective", "gratitude"])
_NEGATIVE_KEYWORDS = set(["frustration", "bad", "stress", "negative", "struggle", "challenge", "lowlights", "problem"])
_NEUTRAL_KEYWORDS = set(["check", "plan", "review", "task", "goal", "meeting", "day", "week"])


def analyze_entry_name(entry_name: str) -> dict:
    """
    Analyzes a journal entry name to extract keywords and infer a basic sentiment.

    Args:
        entry_name: The title/description of the journal entry.

    Returns:
        A dictionary containing extracted keywords and inferred sentiment.
    """
    cleaned_name = re.sub(r'[^\w\s]', '', entry_name).lower()
    words = cleaned_name.split()
    
    keywords = [word for word in words if word not in _STOP_WORDS]

    positive_score = sum(1 for word in keywords if word in _POSITIVE_KEYWORDS)
    negative_score = sum(1 for word in keywords if word in _NEGATIVE_KEYWORDS)

    sentiment = "neutral"
    if positive_score > negative_score:
        sentiment = "positive"
    elif negative_score > positive_score:
        sentiment = "negative"
    
    return {
        "keywords": keywords,
        "sentiment": sentiment
    }

def infer_notion_template(entry_name: str, template_contexts: dict) -> str:
    """
    Infers the most appropriate Notion template for a journal entry based on its description.

    Args:
        entry_name: The title/description of the journal entry.
        template_contexts: A dictionary where keys are template names and values are their descriptions.

    Returns:
        The name of the inferred template, or a default template if no strong match is found.
    """
    if not template_contexts:
        return "Simple Win" # Default if no contexts are provided

    entry_analysis = analyze_entry_name(entry_name)
    entry_keywords = set(entry_analysis["keywords"])
    entry_sentiment = entry_analysis["sentiment"]

    best_match_template = "Simple Win" # Fallback default
    highest_score = -1

    for template_name, template_description in template_contexts.items():
        template_analysis = analyze_entry_name(template_description)
        template_keywords = set(template_analysis["keywords"])
        template_sentiment = template_analysis["sentiment"]

        score = 0

        # Keyword overlap score
        overlap = len(entry_keywords.intersection(template_keywords))
        score += overlap * 2 # Give more weight to keyword overlap

        # Sentiment match score
        if entry_sentiment == template_sentiment and entry_sentiment != "neutral":
            score += 1

        # Specific keyword boosts (e.g., "win" in entry boosts "Simple Win")
        if "win" in entry_keywords and "win" in template_keywords:
            score += 2
        if "gratitude" in entry_keywords and "gratitude" in template_keywords:
            score += 2
        if "frustration" in entry_keywords and "frustration" in template_keywords:
            score += 2
        if "best" in entry_keywords and "best" in template_keywords:
            score += 2

        if score > highest_score:
            highest_score = score
            best_match_template = template_name
        elif score == highest_score and highest_score > 0:
            # If scores are tied, prefer a template that is a better "default"
            # This is a simple tie-breaking rule, could be more sophisticated
            if template_name == "Simple Win":
                best_match_template = template_name

    # If the highest score is still very low, it means no good match was found
    # We can set a threshold or just stick to the default.
    if highest_score <= 1: # Arbitrary low threshold for a weak match
        return "Simple Win" # Return a generic default
    
    return best_match_template


def fill_template_with_args(template_content: str, args: dict) -> str:
    """
    Fills a Markdown template with provided arguments and dynamically generated values.
    Handles Templater-like placeholders.

    Args:
        template_content: The content of the template as a string.
        args: A dictionary of arguments to fill into the template.
              Expected keys: "title", and any keys used in tp.file.arg().

    Returns:
        The filled template content as a string.
    """
    filled_content = template_content

    # Handle tp.file.creation_date
    now = datetime.datetime.now()
    filled_content = re.sub(
        r"<% tp\.file\.creation_date\(\"(.*?)\"\) %>",
        lambda match: now.strftime(match.group(1)),
        filled_content
    )

    # Handle tp.file.arg
    filled_content = re.sub(
        r"<% tp\.file\.arg\(\"(.*?)\"\) %>",
        lambda match: args.get(match.group(1), ""),
        filled_content
    )

    # Handle <%* tR += `${title}` %> and similar title injections
    # Assumes 'title' is in args for this.
    if "title" in args:
        filled_content = re.sub(
            r"<%+\s*tR\s*\+= \`\$\{\\w+\}\`\s*%>+", # Matches <%* tR += `${title}` %>
            lambda match: args.get(match.group(1), ""),
            filled_content
        )
        # Also replace other direct title references in the body if any
        filled_content = filled_content.replace("<h1><%* tR += `${title}` %></h1>", f"# {args['title']}")
        filled_content = filled_content.replace("<%* tR += `${title}` %>", args['title'])


    # Remove Templater-specific control flow (like title renaming or prompting)
    # This is a simplification; a full Templater engine would be complex.
    filled_content = re.sub(r"<%+\s*let title = tp\.file\.title.*?%>+", "", filled_content, flags=re.DOTALL)
    filled_content = re.sub(r"<%+\s*if \(title\.startsWith\(\"Untitled\"\)).*?%>+", "", filled_content, flags=re.DOTALL)
    filled_content = re.sub(r"<%+\s*await tp\.file\.rename\(`\${title}`\).*?%>+", "", filled_content, flags=re.DOTALL)
    filled_content = re.sub(r"<%+\s*await tp\.system\.prompt\('.*?'\).*?%>+", "", filled_content, flags=re.DOTALL)
    
    # Remove <%* tR += "---" %> as it's typically for frontmatter end which we handle
    filled_content = filled_content.replace("<%* tR += \"---\" %>", "")

    # Clean up multiple blank lines
    filled_content = re.sub(r'\n\s*\n', '\n\n', filled_content).strip()

    return filled_content


def load_and_fill_template(template_name: str, args: dict, output_dir: str) -> str:
    """
    Loads a template file, fills it with provided arguments, and saves the result as a new Markdown file.

    Args:
        template_name: The name of the template file (e.g., "human_realm_template.md").
        args: A dictionary of arguments to pass to fill_template_with_args.
              Must include "title" for the new note.
        output_dir: The directory where the new Markdown file should be saved.

    Returns:
        The full path to the newly created Markdown file, or None if an error occurred.
    """
    template_path = os.path.join("Templates", template_name)
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return None

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except Exception as e:
        print(f"Error reading template file {template_path}: {e}")
        return None

    filled_content = fill_template_with_args(template_content, args)

    if "title" not in args or not args["title"]:
        print("Error: 'title' argument is required to save the new note.")
        return None

    filename_title = re.sub(r'[^\w\-_\. ]', '', args["title"]).replace(' ', '_')
    output_file_path = os.path.join(output_dir, f"{filename_title}.md")

    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(filled_content)
        print(f"Successfully created new note from template: {output_file_path}")
        return output_file_path
    except Exception as e:
        print(f"Error saving new note {output_file_path}: {e}")
        return None
