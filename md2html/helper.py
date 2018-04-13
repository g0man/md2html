# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
from markdown import util

def keywords2tag(tag) :
    """
    remove the last number in tag 
    e.g. "span1" to "span"
    """
    i = 0
    for x in tag[::-1] : # reversed checking
        if x.isdigit():
            i += 1
    if i > 0 :
        return tag[:-i]
    else :
        return tag

def add_subelement_list(parent, cfg, tags) :
    """
    go through 'tags', such as ['p1', 'span', 'p2'], then 
    according to 'cfg' get each attributes, build subelement list
    with its attrs

    return the last sub-elment for setting its text
    """

    prev = parent
    for tag in tags:
        attrs = cfg.get(tag)

        cur = util.etree.SubElement(prev, keywords2tag(tag))
        set_tag_attrs(cur, attrs)

        prev = cur

    return prev

def set_tag_attrs(tag, attrs):
    for k, v in attrs.items() :
        tag.set(k, v)
