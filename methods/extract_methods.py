import re
from methods import transform_methods as tm


def extract_between_keywords(text, start_keyword, end_keyword, find_all=False):
    """
    Extract data between 2 keywords in a string,
    if find_all=True then return all found data
    """
    results = []
    start = 0

    while True:
        start_index = text.find(start_keyword, start)
        if start_index == -1:
            break

        end_index = text.find(end_keyword, start_index + len(start_keyword))
        if end_index == -1:
            substring = text[start_index + len(start_keyword) :]
            results.append(substring.strip())
            break

        if end_index > start_index:
            substring = text[start_index + len(start_keyword) : end_index]
            results.append(substring.strip())

        if not find_all:
            return " ".join(results)

        start = end_index + len(end_keyword)
    return results


def find_date(text):
    """Find any kind of dates formats in a string"""
    date_pattern = r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b|\b\d{1,2}[-\s](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-\s]\d{2,4}\b|\b\d{1,2}[-\s](?:January|February|March|April|May|June|July|August|September|October|November|December)[-\s]\d{2,4}\b"
    pattern = re.compile(date_pattern)
    matches = pattern.findall(text)
    return matches


def extract_string(string, start_keyword, end_keyword):
    extracted_data = extract_between_keywords(string, start_keyword, end_keyword)
    return extracted_data


def extract_nested_string(string, keywords_dict):
    keywords = keywords_dict.values()
    for keyword in keywords:
        if keyword == list(keywords)[-1]:
            string = extract_between_keywords(
                str(string), keyword[0], keyword[1], find_all=True
            )
        else:
            string = extract_between_keywords(str(string), keyword[0], keyword[1])
    return string


def extract_dates(string, start_keyword, end_keyword):
    extracted_data = extract_between_keywords(string, start_keyword, end_keyword)
    extracted_data = find_date(extracted_data)
    extracted_data = [tm.transform_date(date) for date in extracted_data]
    return extracted_data
