#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# sys.path.insert(0, '/home/michael/ws/src/github.com/md2html/markdown')
import json
import optparse
import os
import sys

import markdown

import md2html
from md2html import weixin
from md2html.weixin.knb_ext import makeExtension


def parse_options(args=None, values=None):
    """
    Define and parse `optparse` options for command-line usage.
    """
    usage = """%prog [-i INPUT_FILE] [-o OUTPUT_FILE] [-c CONFIG_FILE]"""
    desc = "an weixin mp article layout tool which inspired by [knbknb](可能吧) weixin article layout"
    ver = "%%prog %s" % md2html.__version__

    parser = optparse.OptionParser(usage=usage, description=desc, version=ver)

    parser.add_option("-i", "--input", dest="input_file", default=None,
                      help="specify the Markdown file *.md which will be transfer to html")
    parser.add_option("-o", "--output", dest="output_file", default=None,
                      help="specify the output *.html file which will be transfer to html")
    parser.add_option("-c", "--config", dest="config_file", default=None,
                      help="specify the config file which defines the rules how to subsitute the tags")

    (options, args) = parser.parse_args(args, values)
    # print(options)

    for arg in vars(options):
        filename = getattr(options, arg) # not completing the options 
        if filename is None:
            parser.print_usage()
            sys.exit(1)
        if not os.path.isfile(filename):
            print("invalid file name specified : %s %s " % (arg, filename))
            sys.exit(2)

    return options


def transfer(infile, outfile, cfg) :
    with open(cfg, "r") as f:
        data = json.load(f)

        weixin = makeExtension(configs={'wxcfg' : data})
        markdown.markdownFromFile(input=infile, output=outfile, extensions=[weixin, "markdown.extensions.nl2br"])

        f.close()

if __name__ == '__main__':

    opts = parse_options()
    # transfer("test.md", "output.html", "config/weixin.json")
    transfer(opts.input_file, opts.output_file, opts.config_file)
