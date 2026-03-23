from masking import mask_entities, reinsert_entities
from normalization import deobfuscate_query

def run_demo():
    # Example queries (safe, synthetic)
    queries = [
        "What are the offenses committed by M. Lopez, 36, offenses in Phoenix?",
        "Show crimes by W@ng in Nevada between November 5, 2011 and January 31, 2012",
        "List incidents involving Miss Amanda-Lynn Smith, 42"
    ]

    for i, query in enumerate(queries, 1):
        print("=" * 100)
        print(f"Example {i}")
        
        # Step 1: Normalize (de-obfuscate)
        normalized = deobfuscate_query(query)

        # Step 2: Mask entities
        masked_query, entity_map = mask_entities(normalized)

        # Step 3: Reinsert entities (post-processing)
        restored = reinsert_entities(masked_query, entity_map)

        # Print results
        print(f"Original Query   : {query}")
        print(f"Normalized Query : {normalized}")
        print(f"Masked Query     : {masked_query}")
        print(f"Entity Map       : {entity_map}")
        print(f"Restored Query   : {restored}")
        print("-" * 100)
        print()
        

if __name__ == "__main__":
    run_demo()