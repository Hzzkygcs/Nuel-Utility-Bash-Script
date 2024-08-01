import yaml
import sys

def main(yaml_file, project_name_to_find, new_commit):
    with open(yaml_file) as f:
        document = yaml.safe_load(f)
    projects = document['ml-models']['projects']
    for project in projects:
        if project['name'] == project_name_to_find:
            modify(project, new_commit)
            return
    raise Exception(f"Not found: {project_name_to_find}")



def modify(project, new_commit):
    curr_img = project['image']
    old_img = curr_img
    curr_img = curr_img.split(":")
    curr_img[1] = str(new_commit)
    project['image'] = ":".join(curr_img)


def persist(yaml_file, projects):
    with open(yaml_file) as f:
        yaml.dump(projects, f)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])

