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
    usage = """%prog -i INPUT_FILE -o OUTPUT_FILE -c CONFIG_FILE [-e HEADER_FILE] [-f FOOTER_FILE] """
    desc = "an weixin mp article layout tool which inspired by [knbknb](可能吧) weixin article layout"
    ver = "%%prog %s" % md2html.__version__

    parser = optparse.OptionParser(usage=usage, description=desc, version=ver)

    parser.add_option("-i", "--input", dest="input_file", default=None,
                      help="specify the Markdown file *.md which will be transfer to html")
    parser.add_option("-o", "--output", dest="output_file", default=None,
                      help="specify the output *.html file which will be transfer to html")
    parser.add_option("-c", "--config", dest="config_file", default=None,
                      help="specify the config file which defines the rules how to subsitute the tags")
    parser.add_option("-e", "--header", dest="header_file", default=None,
                      help="specify html header snippet code which will be inserted in the header of [output_file] ")
    parser.add_option("-f", "--footer", dest="footer_file", default=None,
                      help="specify html footer snippet code which will be appended at the end of [output_file] ")

    (options, args) = parser.parse_args(args, values)
    # print(options)

    for arg in vars(options):
        filename = getattr(options, arg) # not completing the options 
        if filename is None:
            if arg == "header_file" or arg == "footer_file" :
                continue # -h & -f are optional
            parser.print_usage()
            sys.exit(1)
        if not os.path.isfile(filename):
            if arg == "output_file":
                d = os.path.dirname(filename)
                if d == '' or os.path.exists(d):
                    continue
            print("invalid file name specified : %s %s " % (arg, filename))
            sys.exit(2)

    return options

def get_reading_minutes(filename):

    with open(filename, "r") as f:
        word_count = len(f.read())
        print("word count: %d" % word_count)
        f.close()

        return int(word_count/700)

    return 0

def transfer(infile, outfile, cfgfile, headerfile, footerfile) :
    with open(cfgfile, "r") as f:
        data = json.load(f)
        
        # default: footer.html/header.html is in the folder which weixin.json is in
        data['__cmd_cfg_path__'] = os.path.dirname(cfgfile)
        if headerfile:
            data['__cmd_header_file__'] = headerfile
        if footerfile:
            data['__cmd_footer_file__'] = footerfile
        data['READING_MINUTES'] = get_reading_minutes(infile)

        weixin = makeExtension(configs={'wxcfg' : data})
        markdown.markdownFromFile(input=infile, output=outfile, extensions=[weixin, "markdown.extensions.nl2br"])

        f.close()

if __name__ == '__main__':

    opts = parse_options()
    # transfer("test.md", "output.html", "config/weixin.json")
    transfer(opts.input_file, opts.output_file, opts.config_file, opts.header_file, opts.footer_file)
