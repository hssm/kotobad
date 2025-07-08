import xml.etree.ElementTree as ET
import random

# misc=6 derog
# misc=28 joc
# misc=25 sens
# misc=24 vulg
# These are the tags we want. Remap them to shorter names.
tags = {
    'derogatory': 'derogatory',
    'jocular, humorous term': 'humorous',
    'sensitive': 'sensitive',
    'vulgar expression or word': 'vulgar'
}

random.seed(7890)

def parse():
    tree = ET.parse('JMdict_e')
    rude_words = get_rude(tree.getroot())
    random.shuffle(rude_words)
    for entry in rude_words:
        kana = entry.find('.//reb').text
        keb = entry.find('.//keb')
        kanji = kana
        if hasattr(keb, 'text'):
            kanji = keb.text

        tagged = get_tagged_senses(entry)
        pretty_rude = get_pretty_senses_rude(tagged)
        pretty_normal = get_pretty_senses_normal(tagged)

        seq = entry.find('.//ent_seq').text
        start = f"---BEGIN---{seq}"
        word = f'{kanji}' if kanji == kana else f"{kanji} [{kana}]"
        stop = "---END---"

        open_post = pretty_rude
        reply_post = ''
        if len(pretty_normal) > 0:
            reply_start = "---REPLY---"
            reply_post = f"\n{reply_start}\n{pretty_normal}"

        print(
f"""
{start}
{word}

{open_post}{reply_post}
{stop}
""", end="")



def get_rude(root):
    """Get a list of all entries that contain at least one of our tags"""
    rude_words = []
    for entry in root.findall('.//entry'):
        added = False
        for sense in entry.findall('.//sense'):
            if added:
                continue
            for misc in sense.findall('.//misc'):
                if misc.text in tags.keys():
                    if added:
                        continue
                    rude_words.append(entry)
                    added = True
    return rude_words


def get_tagged_senses(entry):
    """Given an entry, return a list of all senses, annotated with which of our tags they match."""
    senses = []
    for sense in entry.findall('.//sense'):
        miscs = []
        glosses = []
        for misc in sense.findall('.//misc'):
            if misc.text in tags.keys():
                miscs.append(tags[misc.text])

        for gloss in sense.findall('.//gloss'):
            glosses.append(gloss.text)
        senses.append({'tags': miscs, 'glosses': glosses})

    return senses

def get_pretty_senses_rude(tagged):
    pretty = ""
    grouped = {}
    for sense in tagged:
        if len(sense['tags']) > 0:
            tag_complete = ', '.join(sense['tags'])
            if not tag_complete in grouped:
                grouped[tag_complete] = []
            grouped[tag_complete].append(sense['glosses'])

    for tag, glosses in grouped.items():
        pretty += f"[{tag}]\n"
        prefix = "- " if len(glosses) > 1 else ""
        for gloss in glosses:
            gloss_line = '; '.join(gloss)
            pretty += f"{prefix}{gloss_line}\n"

    return pretty.strip()

def get_pretty_senses_normal(tagged):
    pretty = ""
    grouped = {}
    for sense in tagged:
        if len(sense['tags']) == 0:
            tag_complete = 'other meanings'
            if not tag_complete in grouped:
                grouped[tag_complete] = []
            grouped[tag_complete].append(sense['glosses'])

    for tag, glosses in grouped.items():
        pretty += f"[{tag}]\n"
        prefix = "- " if len(glosses) > 1 else ""
        for gloss in glosses:
            gloss_line = '; '.join(gloss)
            next = f"{prefix}{gloss_line}\n"
            if len(pretty + next + "[+more]") >= 295:
                pretty += "[+more]"
                break
            pretty += next

    return pretty.strip()



if __name__ == "__main__":
    parse()
