import sys
import json
import re
import argparse

FIELDS_TO_CHECK = {
    '@article': 'journal',
    '@book': 'publisher',
    '@inproceedings': 'publisher',
    # ... add more mappings as needed ...
}

def check_and_abbreviate(line, field_type, abbreviations):
    # Extract the field value
    match = re.search('".*"', line) or re.search('{.*}', line)
    if not match:
        return line
    field_value = match.group(0)[1:-1]
    
    # If the field value is missing from the abbreviation dictionary, add to missing list
    if field_value not in abbreviations:
        missing_fields.add(field_value)
        return line

    # Replace with abbreviation from dictionary
    abbreviated_value = abbreviations[field_value]
    return line.replace(field_value, abbreviated_value)

missing_fields = set()

def extract_journal_name(line):
    if re.search('".*"', line) is not None:
        journal_str = re.search('".*"', line).group(0)
    elif re.search('{.*}', line) is not None:
        journal_str = re.search('{.*}', line).group(0)
    else:
        return None
    journal_name = journal_str[1:-1].replace('{','').replace('}','').lower()
    return journal_name

def abbreviate(line, journal_to_abbr):
    if re.search('".*"', line) is not None:
        journal_name_template = '"{}"'
        journal_str = re.search('".*"', line).group(0)
    elif re.search('{.*}', line) is not None:
        journal_name_template = '{{{}}}'
        journal_str = re.search('{.*}', line).group(0)
    else:
        raise ValueError('the format "{}" is not valid'.format(line))
    journal_name_strip = journal_str[1:-1]
    journal_name = journal_name_strip.replace('{','').replace('}','')
    journal_name = journal_to_abbr.get(journal_name.lower(), journal_name_strip)
    journal_name = journal_name_template.format(journal_name)

    return line.replace(journal_str, journal_name)
# This code valid for journals only and has been commented for the love of god.
# def main(journal_to_abbr):
#     missing_journals = set()
#     for line in sys.stdin:
#         line_strip = line.strip()
#         if line_strip.startswith('journal'):
#             journal_name = extract_journal_name(line)
#             if journal_name and journal_name not in journal_to_abbr:
#                 missing_journals.add(journal_name)
#             new_line = abbreviate(line, journal_to_abbr)
#             print(new_line.rstrip())
#         else:
#             print(line.rstrip())

#     # At the end, write missing journals to a txt file
#     with open("data/missing_journals.txt", "w") as outfile:
#         outfile.write("Missing Journals:\n")
#         for journal in missing_journals:
#             outfile.write(journal + "\n")
            
def main(abbreviations):
    for line in sys.stdin:
        line_strip = line.strip()
        for entry_type, field in FIELDS_TO_CHECK.items():
            if line_strip.startswith(field):
                new_line = check_and_abbreviate(line, field, abbreviations)
                print(new_line.rstrip())
                break
        else:
            print(line.rstrip())

    # At the end, write missing fields to a txt file in the 'data' directory
    with open("data/missing_fields.txt", "w") as outfile:
        outfile.write("Missing Fields:\n")
        for field in missing_fields:
            outfile.write(field + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Journal abbreviation")
    parser.add_argument('--user-json', type=str, default=None, help="customized json file")
    args = parser.parse_args()

    with open('journals.json') as fin:
        journal_to_abbr = json.load(fin)

    if args.user_json is not None:
        with open(args.user_json) as fin:
            customize_json = json.load(fin)
        journal_to_abbr.update(customize_json)

    journal_to_abbr = {k.lower(): v for k, v in journal_to_abbr.items()} 

    main(journal_to_abbr)
