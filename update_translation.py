from collections import defaultdict
import csv
import glob
import os
import subprocess
from translation_storage import TranslationFile, TranslationEntry, load_translation

from config import *


def update_mod_repo():
    if not os.path.exists(MOD_REPO_NAME):
        subprocess.call(["git", "clone", MOD_REPO_URL])
    
    subprocess.call(["git", "pull"], cwd=os.path.realpath(MOD_REPO_NAME))


def read_translationfile(path: str) -> dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    result = {}
    for line in lines:
        k, v = line.split("=", maxsplit=1)
        result[k] = v[:-1]
    
    return result


def generate_templates() -> dict[str, dict[str, str]]:
    base_dir = os.path.join(MOD_REPO_NAME, MOD_REPO_NAME, "Translations", "en")

    result: defaultdict[str, dict[str, str]] = defaultdict(dict)

    for txt_path in glob.glob(f"{base_dir}/**/*.txt", recursive=True):
        relpath = os.path.relpath(txt_path, base_dir)
        category = relpath.split(os.path.sep)[0].removesuffix(".txt").removesuffix("-en")

        data = read_translationfile(txt_path)
        result[category].update(data)
    
    return result


def merge(output_path, template_data: dict[str, str], translation_data: dict[str, TranslationEntry]):
    template = TranslationFile()
    for key, source in template_data.items():
        template.append(TranslationEntry(key=key, source=source))

    tr = TranslationFile()
    tr.extend(filter(lambda x: x.key in template_data, translation_data.values()))

    if len(tr) == 0:
        template.export(output_path)
        return

    merged = template.merge(tr)
    if merged:
        template.export(output_path)


def update(filename, template_data, translation_data):
    po_name = os.path.splitext(filename)[0] + ".po"
    output_path = os.path.join(TRANSLATION_DIRECTORY, LANGCODE, po_name)

    merge(output_path, template_data, translation_data)


def main():
    os.makedirs(os.path.join(TRANSLATION_DIRECTORY, LANGCODE), exist_ok=True)

    update_mod_repo()

    templates = generate_templates()

    translation_data = load_translation(os.path.join(TRANSLATION_DIRECTORY, LANGCODE))

    for filename in templates:
        update(filename, templates[filename], translation_data)


if __name__ == '__main__':
    main()