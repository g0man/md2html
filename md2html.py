#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# sys.path.insert(0, '/home/michael/ws/src/github.com/md2html/markdown')
import json
import sys

import markdown

import md2html
from md2html import weixin
from md2html.weixin.knb_ext import makeExtension


def transfer(infile, outfile, cfg) :
    with open(cfg, "r") as f:
        data = json.load(f)

        weixin = makeExtension(configs={'wxcfg' : data})
        markdown.markdownFromFile(input=infile, output=outfile, extensions=[weixin, "markdown.extensions.nl2br"])

        f.close()

if __name__ == '__main__':

    transfer("test.md", "output.html", "config/weixin.json")
