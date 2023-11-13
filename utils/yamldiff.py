#!/usr/bin/env python
import yaml
import os
import sys
import subprocess
import argparse


def load_file(file_name):
    try:
        with open(file_name, 'r') as fo:
            content = fo.read()
            return yaml.load(content, Loader=yaml.Loader)
    except FileNotFoundError:
        return None

def get_git_show_output(file_reference, verbose=True):
    # Construct the git show command with the input commit hash
    command = ['git', 'show', file_reference]
    if verbose:
        print("Loading file from git: ", file_reference)
    try:
        # Run the command and capture the output
        result = subprocess.check_output(command, universal_newlines=True)

        # Return the output
        return yaml.load(result, Loader=yaml.Loader)
    except subprocess.CalledProcessError as e:
        # Handle errors, if any
        print(f"Error: {e}")
        return None


atoms = [str, int, float]

def diff(a, b):
    if a == b:
        # no difference in this subtree
        return None
    elif type(a) == type(b):
        # iterate though a/b to find where the difference is
        if type(a) in atoms:
            return a, b
        else:
            return iterate_diff(a, b)
    else:
        # if the type of a and b are different, all descendents are a diff
        return a, b # old, new

def iterate_diff(a, b):
    # Precondition: a,b are same type (list or dict)

    if type(a) == list:
        # TODO: compute optimal alignment
        N = max(len(a), len(b))
        diffsa = []
        diffsb = []
        for ix in range(N):
            if ix < len(a) and ix < len(b):
                d = diff(a[ix], b[ix])
                if d is not None:
                    diffsa.append(d[0])
                    diffsb.append(d[1])
            elif ix < len(a):
                diffsa.append(a[ix])
            else:
                diffsb.append(b[ix])
        return diffsa, diffsb

    elif type(a) == dict:
        diffsa = {}
        diffsb = {}
        for k in set(a.keys()).union(set(b.keys())):
            if k in a.keys() and k in b.keys():
                d = diff(a[k], b[k])
                if d is not None:
                    diffsa[k] = d[0]
                    diffsb[k] = d[1]
            elif k in a.keys():
                # key in a and not b
                diffsa[k] = a[k]
            else:
                # key in b and not a
                diffsb[k] = b[k]

        return diffsa, diffsb

def get_yaml_lines(y):
    lines = []
    if type(y) == dict:
        for k in sorted(y.keys()):
            if y[k] == {}:
                continue
            lines.append(f"{k}:")
            children = get_yaml_lines(y[k])
            lines += ["  " + l for l in children]
        return lines
    if type(y) == list:
        for e in y:
            child_lines = get_yaml_lines(e)
            if len(child_lines) > 0:
                lines += ["  - " + child_lines[0]]
                lines += ["    " + cl for cl in child_lines[1:]]
        return lines
    if y is None:
        return []
    # atom
    return [str(y)]


# Setup argparse to handle command-line arguments
parser = argparse.ArgumentParser(description='Process two files or files at commit hash (i.e. <HASH>:path/relative/to/git/base/dir')
parser.add_argument('file1', help='First file name or git-relative path at hash')
parser.add_argument('file2', help='Second file name or git-relative path at hash')

args = parser.parse_args()

y1 = load_file(args.file1) or get_git_show_output(args.file1)
y2 = load_file(args.file2) or get_git_show_output(args.file2)

# Do something with the loaded content
if y1 is None:
    print(f"Could not load file1: {args.file1}")

if y2 is None:
    print(f"Could not load file2: {args.file2}")

if y1 is None or y2 is None:
    exit(0)

out = diff(y1, y2)
if out is None:
    print("No diff")
    exit(1)
with open("/tmp/yaml_old.yaml", "w") as fo:
    for l in get_yaml_lines(out[0]):
        fo.write(l + "\n")
with open("/tmp/yaml_new.yaml", "w") as fo:
    for l in get_yaml_lines(out[1]):
        fo.write(l + "\n")

print("")
print(args.file1 + " " * max((40 - len(args.file1)),1) + args.file2)
print("-"*80)
os.system("diff -y -d --color %s %s" % ("/tmp/yaml_old.yaml", "/tmp/yaml_new.yaml"))
