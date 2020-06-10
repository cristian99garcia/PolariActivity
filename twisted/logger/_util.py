# -*- test-case-name: twisted.logger.test.test_util -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Logging utilities.
"""



def formatTrace(trace):
    """
    Format a trace (that is, the contents of the C{log_trace} key of a log
    event) as a visual indication of the message's propagation through various
    observers.

    @param trace: the contents of the C{log_trace} key from an event.
    @type trace: object

    @return: A multi-line string with indentation and arrows indicating the
        flow of the message through various observers.
    @rtype: L{unicode}
    """
    def formatWithName(obj):
        if hasattr(obj, "name"):
            return "{0} ({1})".format(obj, obj.name)
        else:
            return "{0}".format(obj)

    result = []
    lineage = []

    for parent, child in trace:
        if not lineage or lineage[-1] is not parent:
            if parent in lineage:
                while lineage[-1] is not parent:
                    lineage.pop()

            else:
                if not lineage:
                    result.append("{0}\n".format(formatWithName(parent)))

                lineage.append(parent)

        result.append("  " * len(lineage))
        result.append("-> {0}\n".format(formatWithName(child)))

    return "".join(result)