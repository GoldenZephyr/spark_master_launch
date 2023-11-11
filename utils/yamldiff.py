import yaml
import os
import sys

atoms = [str, int, float]

args = sys.argv

if len(args) != 3:
    print("Usage: yamldiff.py <old config yaml> <new config yaml>")
    exit(1)

fn_a = args[1]
fn_b = args[2]

with open(fn_a, "r") as fo:
    y1 = yaml.load(fo,Loader=yaml.Loader)
with open("/tmp/yaml_old.yaml", "w") as fo:
    fo.write(yaml.dump(y1))

with open(fn_b, "r") as fo:
    y2 = yaml.load(fo,Loader=yaml.Loader)
with open("/tmp/yaml_new.yaml", "w") as fo:
    fo.write(yaml.dump(y2))

print("")
print(fn_a + " " * max((40 - len(fn_a)),1) + fn_b)
print("-"*80)
os.system("diff -y --suppress-common-lines --color %s %s" % ("/tmp/yaml_old.yaml", "/tmp/yaml_new.yaml"))


def diff(a, b):
    if a == b:
        # no difference in this subtree
        return ()
    elif type(a) == type(b):
        # iterate though a/b to find where the difference is
        if type(a) in atoms:
            print("found atoms:", a, b)
            return a, b
        else:
            print("found composites:", a, b)
            return iterate_diff(a, b)
    else:
        # if the type of a and b are different, all descendents are a diff
        return a, b # old, new


def iterate_diff(a, b):
    # Precondition: a,b are same type (list or dict)

    if type(a) == list:
        # TODO: compute optimal alignment
        N = max(len(a), len(b))
        diffs = ()
        for ix in range(N):
            if ix < len(a) and ix < len(b):
                diffs += (diff(a[ix], b[ix]),)
            elif ix < len(a):
                diffs += ((a, None),)
            else:
                diffs += ((None, b),)
        return diffs

    elif type(a) == dict:
        diffs = {}
        for k in set(a.keys()).union(set(b.keys())):
            if k in a.keys() and k in b.keys():
                diffs[k] = diff(a[k], b[k])
            elif k in a.keys():
                # key in a and not b
                diffs[k] = (a[k], None)
            else:
                # key in b and not a
                diffs[k] = (None, b[k])

        return diffs
#
#def yaml_to_lines(snip):
#    yml = yaml.dump(snip).split('\n')
#    return [y for y in yml if len(y) > 0]
#
#def get_diff_string(d, diff_idx):
#    if type(d) == tuple:
#        if d == ():
#            # no diff
#            return None, None
#
#        if (d[diff_idx] is None):
#            return None, None
#
#        if diff_idx == 0 and d[1] is None:
#            if type(d[0]) in atoms:
#                lines = [str(d[0])]
#            else:
#                lines = yaml_to_lines(d[0])
#            prefixes = ['DEL']*len(lines)
#            return prefixes, lines
#
#        if diff_idx == 1 and d[0] is None:
#            if type(d[1]) in atoms:
#                lines = [str(d[1])]
#            else:
#                lines = yaml_to_lines(d[1])
#            prefixes = ['ADD']*len(lines)
#            return prefixes, lines
#
#        if type(d[0]) != type(d[1]):
#            lines = yaml_to_lines(d[diff_idx])
#            if diff_idx == 0:
#                prefixes = ["OLD"]*len(lines)
#            else:
#                prefixes = ["NEW"]*len(lines)
#            return prefixes, lines
#
#        if len(d) == 2 and (type(d[0]) in atoms or type(d[1]) in atoms):
#            return [["OLD", "NEW"][diff_idx]], [d[diff_idx]]
#
#        pfx = []
#        lines = []
#        for t in d:
#            p,l = get_diff_string(t, diff_idx)
#            if p is None:
#                continue
#            pfx += p
#            lines += ["  " + line for line in l]
#        return pfx, lines
#
#    elif type(d) == dict:
#        pfx = []
#        lines = []
#        for k,v in d.items():
#            if v == ():
#                continue
#
#            p, l = get_diff_string(v, diff_idx)
#            if p is None:
#                continue
#            pfx.append("   ")
#            lines.append(k + ":")
#            pfx += p
#            lines += ["  " + line for line in l]
#
#        return pfx, lines
#
#    #elif type(d) == list:
#    #    pass
#
#def print_diff(d):
#    p1, l1 = get_diff_string(d, 0)
#    for p,l in zip(p1,l1):
#        print(p + "  " + l)
#    p2, l2 = get_diff_string(d, 1)
#    print('====')
#    for p,l in zip(p2,l2):
#        print(p + "  " + l)

out = diff(y1, y2)
print(out)
#print_diff(out)




