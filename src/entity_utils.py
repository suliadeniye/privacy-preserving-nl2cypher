import re

HONORIFICS = {"mr", "mrs", "miss", "ms", "dr", "prof", "sir"}
SUFFIXES = {"jr", "sr", "ii", "iii", "iv"}

known_states = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
}

def expand_person_spans(doc):
    updated_ents = []

    for ent in doc.ents:
        if ent.label_ != "PERSON":
            updated_ents.append(ent)
            continue

        start = ent.start
        end = ent.end

        # Expand left if title exists before
        if start > 0:
            prev_token = doc[start - 1]
            if prev_token.text.lower().strip(".") in HONORIFICS:
                start -= 1

        # Expand right if suffix follows
        if end < len(doc):
            next_token = doc[end]
            if next_token.text.lower().strip(".") in SUFFIXES:
                end += 1

        # Create new span with expanded range
        new_ent = doc[start:end]
        new_ent.label_ = "PERSON"
        updated_ents.append(new_ent)

    # Update doc.ents with modified spans
    doc.ents = updated_ents
    return doc

def classify_gpe_entity(entity_text):
    """
    Determines if a GPE (Geopolitical Entity) is a city or a state.
    """
    return "STATE" if entity_text in known_states else "CITY"

def is_age_reference(entity_text):
    """
    Determines if a text is referring to an age rather than a date.
    """
    #return any(keyword in entity_text.lower() for keyword in ["years old", "years of age", "aged", "-year-old"])
    return bool(re.search(r"\b\d+\s*(years|years old|years of age|-year-old)\b", entity_text.lower()))

def extract_numeric_age(entity_text):
    """
    Extracts only the numeric portion of an age reference.
    Example: "100 years old" -> "100"
    """
    match = re.search(r"\b\d+\b", entity_text)
    return match.group(0) if match else entity_text  # Return numeric portion if found, else original text

