import sys
import json
import re

FIELDS_TO_CHECK = {
    '@article': 'journal',
    '@book': 'publisher',
    '@inproceedings': 'publisher',
    '@incollection': 'booktitle',
    '@misc': 'howpublished',  # 'howpublished' might be used, but 'misc' entries can vary greatly
    '@techreport': 'institution',
    # ... add more mappings as needed ...
}


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

def main(abbreviations):
    for line in sys.stdin:
        line_strip = line.strip()
        for entry_type, field in FIELDS_TO_CHECK.items():
            if line_strip.startswith(field):
                #new_line = check_and_abbreviate(line, field, abbreviations)
                journal_name = extract_journal_name(line)
                if journal_name not in journal_to_abbr:
                    missing_fields.add(journal_name)
                new_line = abbreviate(line, journal_to_abbr)
                print(new_line.rstrip())
                break # don't print the full journal name (else statement) if found
        else:
            print(line.rstrip())

    # At the end, write missing fields to a txt file in the 'data' directory
    with open("data/missing_fields.txt", "w") as outfile:
        outfile.write("Missing Fields:\n")
        for field in missing_fields:
            outfile.write(field + "\n")


if __name__ == '__main__':
    with open('journals.json') as fin:
        journal_to_abbr = json.load(fin)

    journal_to_abbr = {k.lower(): v for k, v in journal_to_abbr.items()} 

    main(journal_to_abbr)