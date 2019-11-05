# Author: Peter Hoffmann
# Fetched from: http://peter-hoffmann.com/2010/extrinsic-visitor-pattern-python-inheritance.html
# and edited for CamelCase

class Visitor(object):
    def visit(self, node, *args, **kwargs):
        meth = None
        for cls in node.__class__.__mro__:
            methName = 'visit' + cls.__name__
            meth = getattr(self, methName, None)
            if meth:
                break

        if not meth:
            meth = self.genericVisit
        return meth(node, *args, **kwargs)
