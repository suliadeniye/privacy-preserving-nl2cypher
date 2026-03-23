
from collections import defaultdict
import re
import spacy
from entity_utils import expand_person_spans, extract_numeric_age, classify_gpe_entity, is_age_reference

nlp = spacy.load("en_core_web_trf")

def mask_entities(query: str):
    masked_query = query
    entity_map = defaultdict(list)

    # === Step 1: Pre-mask AGE via regex BEFORE running SpaCy ===
    age_patterns = [
        r"\bage\s*(\d{1,3})\b",
        r"\baged\s+(\d{1,3})\b",
        r"\b(\d{1,3})\s*(?:years old|yrs old|y/o|yo)\b",
        r"\b(\d{1,3})[-\s]?year[-\s]?old\b",
        r"\b(\d{1,3})\s*yrs\b",
        r"\b(\d{1,3})\s*years\s*of\s*age\b",
        r"\b([A-Z][a-zA-Z\.\-']+(?:\s[A-Z][a-zA-Z\.\-']+)*),\s*(\d{2})(?=,)"
    ]
    
    def age_replacer(match):
        # If pattern has one capturing group → extract from group(1)
        if match.lastindex == 1:
            age_val = match.group(1)
        # If pattern has two capturing groups → extract from group(2)
        elif match.lastindex == 2:
            age_val = match.group(2)
        else:
            return match.group(0)  # do nothing
        
        # Filter out non-age integers
        if not (10 <= int(age_val) <= 99):
            return match.group(0)

        placeholder = f"[AGE_{len(entity_map['AGE']) + 1}]"
        entity_map["AGE"].append(age_val)

        # For patterns matching ", NAME, AGE," → preserve name text if group(1) exists
        if match.lastindex == 2:
            name = match.group(1)
            return f"{name}, {placeholder}"

        # Otherwise just replace the numeric age
        return placeholder


    for pattern in age_patterns:
        masked_query = re.sub(pattern, age_replacer, masked_query, flags=re.IGNORECASE)
    
    # === Step 2: Run SpaCy AFTER masking AGE ===
    doc = nlp(masked_query)
    
    doc = expand_person_spans(doc)

    for ent in doc.ents:
        ent_text = ent.text
        if ent_text.startswith("[AGE_"):  # Already masked
            continue

        if ent.label_ in ["PERSON", "GPE", "DATE", "ORG"]:
            if ent.label_ == "GPE":
                entity_type = classify_gpe_entity(ent_text)
            elif ent.label_ == "DATE":
                entity_type = "AGE" if is_age_reference(ent_text) else "DATE"
            else:
                entity_type = ent.label_

            placeholder = f"[{entity_type}_{len(entity_map[entity_type]) + 1}]"
            entity_map[entity_type].append(ent_text)
            masked_query = masked_query.replace(ent_text, placeholder, 1)

    return masked_query, dict(entity_map)


def reinsert_entities(cypher_query, entity_map):
    """
    Reinserts the original entity names into the generated Cypher query.
    Ensures placeholders are replaced correctly.
    """
    for entity_type, values in entity_map.items():
        for i, value in enumerate(values, start=1):
            placeholder = f"[{entity_type}_{i}]"

            # Ensure AGE values are numeric before reinsertion
            if entity_type == "AGE":
                value = extract_numeric_age(value)  # Convert "100 years old" -> "100"

            cypher_query = cypher_query.replace(placeholder, value, 1)  # Ensure correct sequential replacement

    return cypher_query