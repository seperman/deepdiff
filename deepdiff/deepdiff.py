import difflib
import datetime
from collections import Iterable
# from copy import deepcopy

class DeepDiff(object):
    """
from ddiff import DDiff

t1 = "Haha\nso cool!\nThis is AWSOME!!\n\n\nEnd"
t2 = "Haha!!\nso cool!\nThis is Awesome!!\n\n\nEnd"

ddiff = DDiff()
ddiff.diffit(t1, t2)
print ddiff.changes
"""

    def __init__(self, t1, t2):
        # import collections
        # initial_change_dict={"type_changes":[], "keys_added":[], "keys_removed":[], "values_changed":[]}
        # self.changes = deepcopy(initial_change_dict)
        self.changes = {"type_changes":[], "keys_added":[], "keys_removed":[], "values_changed":[], "unprocessed":[], "list_added":[], "list_removed":[]}
        
        self.diffit(t1, t2)

        self.changes = dict((k, v) for k, v in self.changes.iteritems() if v)


    def diffdict(self, t1, t2, parent):
        t2_keys, t1_keys = [
            set(d.keys()) for d in (t2, t1)
        ]
    
        t_keys_intersect = t2_keys.intersection(t1_keys)

        t_keys_added = t2_keys - t_keys_intersect
        t_keys_removed = t1_keys - t_keys_intersect

        if t_keys_added:
            self.changes["keys_added"].append("%s.%s" % (parent, t_keys_added))

        if t_keys_removed:
            self.changes["keys_removed"].append("%s.%s" % (parent, t_keys_removed))

        for item in t_keys_intersect:
            self.diffit(t1[item], t2[item], parent="%s.%s" % (parent, item))



    def diffit(self, t1, t2, parent=""):

        if type(t1) != type(t2):
            self.changes["type"].append("%s: type change in %s vs. %s" % (parent, t1, t2))

        elif isinstance(t1, basestring):
            diff = difflib.unified_diff(t1.splitlines(), t2.splitlines(), lineterm='')
            diff = list(diff)
            if diff:
                diff = '\n'.join(diff)
                self.changes["values_changed"].append("%s:\n%s" % (parent, diff))
            

        elif isinstance(t1, datetime.datetime):
            if t1 != t2:
                self.changes["values_changed"].append("%s: %s to %s" % (parent, t1, t2))
            
        
        elif isinstance(t1, dict):
            self.diffdict(t1, t2, parent)

        elif isinstance(t1, Iterable):
        #     the_feed[:] = filter(lambda x: x, the_feed)

            items_added = list(set(t2) - set(t1))
            items_removed = list(set(t1) - set(t2))

            if items_added:
                self.changes["list_added"].append( "%s: %s" % (parent, items_added) )

            if items_removed:
                self.changes["list_removed"].append( "%s: %s" % (parent, items_removed) )

        else:
            try:
                t1_dict = t1.__dict__
                t2_dict = t2.__dict__
            except AttributeError:
                pass
            else:
                self.diffdict(t1_dict, t2_dict, parent)

        return



t1 = "Haha\nso cool!\nThis is AWSOME!!\n\n\nEnd"
t2 = "Haha\nso cool!\nThis is AWSOME!!\n\n\nEnd"
# t2 = "Haha!!\nso cool!\nThis is Awesome!!\n\n\nEnd"

ddiff = DeepDiff(t1, t2)
# ddiff.diffit(t1, t2)
print ddiff.changes
