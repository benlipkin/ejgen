import collections
import itertools
import json

import pandas as pd


def format_long_data(data):
    table = collections.defaultdict(list)
    for _, row in data.iterrows():
        objects = sorted(set(o.strip() for o in row[0].split(";")))
        categories = sorted(set(c.strip() for c in row[1].split(";")))
        for o, c in itertools.product(objects, categories):
            table["object"].append(o)
            table["category"].append(c)
    return pd.DataFrame(table)


def compile_prompt():
    ostream = ""
    ostream += "In the following task, you will be presented with an instance of an object and a category.\n"
    ostream += "Your task is to determine whether the object belongs to the category.\n"
    ostream += "You may respond with either 'yes' or 'no'.\n"
    ostream += "\n"
    ostream += "Object:\ntree\n"
    ostream += "Category:\nplant\n"
    ostream += "Response:\nyes\n"
    return ostream


def compile_task(data):
    jsds = {}
    jsds["pretext"] = ""
    jsds["context"] = []
    for _, row in data.iterrows():
        jsds["context"].append(
            {
                "text": f"Object:\n{row['object']}\nCategory:\n{row['category']}",
                "expected": -1,
            }
        )
    jsds["posttext"] = "Response:"
    jsds["queries"] = ["yes", "no"]
    return jsds


def main():
    gsheet = "https://docs.google.com/spreadsheets/d/1YGLXLAyQr-H3tLHALRCdHomOwwKbu9SkDZ1tEdAC02U/export?gid=487192206&format=csv"
    data = pd.read_csv(gsheet, header=None)
    data = format_long_data(data)
    data.to_csv("../materials/norm_samples.csv", index=False)
    prompt = compile_prompt()
    task = compile_task(data)
    with open("../materials/norm.txt", "w") as f:
        f.write(prompt)
    with open("../materials/norm_all.json", "w") as f:
        json.dump(task, f, indent=4)


if __name__ == "__main__":
    main()
