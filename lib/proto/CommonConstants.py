THOUSANDS_SEPARATOR = ' '
ALLOWED_CHARS = set([chr(x) for x in xrange(128)
                     if x not in set(range(9) + [11, 12] + range(14, 32) + [127])])
