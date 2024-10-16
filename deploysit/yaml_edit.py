#!/usr/bin/env python3

from io import StringIO
import yaml

# Initialize YAML object
import sys

def main(yaml_file, project_name_to_find, new_commit):
    with open(yaml_file) as f:
        document = yaml.safe_load(f)
    projects = document['ml-models']['projects']
    for project in projects:
        if project['name'] == project_name_to_find:
            old_img, new_img = modify(project, new_commit)
            persist(yaml_file, old_img, new_img)
            print(f"{get_commit_hash(old_img)} -> {get_commit_hash(new_img)}")
            return
    raise Exception(f"Not found: {project_name_to_find}")


def get_commit_hash(string: str):
    return string.split(":")[1]


def modify(project, new_commit):
    curr_img = project['image']
    old_img = curr_img
    curr_img = curr_img.split(":")
    curr_img[1] = str(new_commit)
    new_img = ":".join(curr_img)
    return old_img, new_img


def persist(yaml_file, old_img, new_img):
    with open(yaml_file, "r") as f:
        old_content = f.read()
    if old_content.count(old_img) > 1:
        msg = f"More than one occurrence of {old_img} in {yaml_file}"
        print(msg)
        sys.exit(1)
        return
    if old_img == new_img:
        print("===> Old and new image are the same")
        sys.exit(1)
        return
    new_content = old_content.replace(old_img, new_img)
    with open(yaml_file, "w") as f:
        f.write(new_content)



if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])

