import re


def transform_level1_header(md_content):
    return re.sub(r'^( *)#(?!#)\s+', r'\1@!@ ', md_content, flags=re.MULTILINE)
