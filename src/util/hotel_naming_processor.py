def preprocess_name(hotel_name):
    # Remove common terms and return keywords
    common_terms = ['inn', 'hotel', 'lodge', 'resort']
    keywords = [word.lower() for word in hotel_name.split() if word.lower() not in common_terms]
    return ' '.join(keywords)


def name_similarity(name1, name2):
    # Calculate similarity score between two preprocessed names
    name1_keywords = set(preprocess_name(name1).split())
    name2_keywords = set(preprocess_name(name2).split())
    # Use Jaccard similarity measure
    intersection = name1_keywords.intersection(name2_keywords)
    union = name1_keywords.union(name2_keywords)
    return len(intersection) / len(union) if len(union) > 0 else 0
