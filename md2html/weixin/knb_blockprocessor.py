# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# got code from python-markdown: markdown/blockprocesser.py, changed it as i wanted

import logging
import re

from markdown import util
from markdown.blockprocessors import BlockProcessor

from .. import helper

logger = logging.getLogger('weixin/blockprocessor')

class OListProcessor(BlockProcessor):
    """ Process ordered list blocks. """

    TAG = 'ol'
    # The integer (python string) with which the lists starts (default=1)
    # Eg: If list is intialized as)
    #   3. Item
    # The ol tag will get starts="3" attribute
    STARTSWITH = '1'
    # List of allowed sibling tags.
    SIBLING_TAGS = ['ol', 'ul']

    def __init__(self, parser, cfg):
        super(OListProcessor, self).__init__(parser)
        self.cfg = cfg
        # Detect an item (``1. item``). ``group(1)`` contains contents of item.
        self.RE = re.compile(r'^[ ]{0,%d}\d+\.[ ]+(.*)' % (self.tab_length - 1))
        # Detect items on secondary lines. they can be of either list type.
        self.CHILD_RE = re.compile(r'^[ ]{0,%d}((\d+\.)|[*+-])[ ]+(.*)' %
                                   (self.tab_length - 1))
        # Detect indented (nested) items of either type
        self.INDENT_RE = re.compile(r'^[ ]{%d,%d}((\d+\.)|[*+-])[ ]+.*' %
                                    (self.tab_length, self.tab_length * 2 - 1))

    def test(self, parent, block):
        return bool(self.RE.match(block))

    def run(self, parent, blocks):
        # Check fr multiple items in one block.
        items = self.get_items(blocks.pop(0))
        sibling = self.lastChild(parent)

        if sibling is not None and sibling.tag in self.SIBLING_TAGS:
            # Previous block was a list item, so set that as parent
            lst = sibling
            # make sure previous item is in a p- if the item has text,
            # then it isn't in a p
            if lst[-1].text:
                # since it's possible there are other children for this
                # sibling, we can't just SubElement the p, we need to
                # insert it as the first item.
                p = util.etree.Element('p')
                p.text = lst[-1].text
                lst[-1].text = ''
                lst[-1].insert(0, p)
            # if the last item has a tail, then the tail needs to be put in a p
            # likely only when a header is not followed by a blank line
            lch = self.lastChild(lst[-1])
            if lch is not None and lch.tail:
                p = util.etree.SubElement(lst[-1], 'p')
                p.text = lch.tail.lstrip()
                lch.tail = ''

            # parse first block differently as it gets wrapped in a p.
            li = util.etree.SubElement(lst, 'li')
            self.parser.state.set('looselist')
            firstitem = items.pop(0)
            self.parser.parseBlocks(li, [firstitem])
            self.parser.state.reset()
        elif parent.tag in ['ol', 'ul']:
            # this catches the edge case of a multi-item indented list whose
            # first item is in a blank parent-list item:
            # * * subitem1
            #     * subitem2
            # see also ListIndentProcessor
            lst = parent
        else:
            # This is a new list so create parent with appropriate tag.

            ## michael.wu added ---
            lst = helper.add_subelement_list(parent, self.cfg, ['blockquote', 'ol'])
            # lst = util.etree.SubElement(parent, self.TAG)
            ## michael.wu added +++

            # Check if a custom start integer is set
            if not self.parser.markdown.lazy_ol and self.STARTSWITH != '1':
                lst.attrib['start'] = self.STARTSWITH

        self.parser.state.set('list')
        # Loop through items in block, recursively parsing each with the
        # appropriate parent.
        for item in items:
            if item.startswith(' '*self.tab_length):
                # Item is indented. Parse with last item as parent
                self.parser.parseBlocks(lst[-1], [item])
            else:
                # New item. Create li and parse with it as parent
                li = util.etree.SubElement(lst, 'li')
                ## michael.wu added ---
                self.add_li_subelment_item(li, item)
                # self.parser.parseBlocks(li, [item])
                ## michael.wu added +++
        self.parser.state.reset()

    def add_li_subelment_item(self, li, text) :
        li_cfg = self.cfg.get('li')
        span = helper.add_subelement_list(li, li_cfg, ['p', 'span'])
        span.text = text

    def get_items(self, block):
        """ Break a block into list items. """
        items = []
        for line in block.split('\n'):
            m = self.CHILD_RE.match(line)
            if m:
                # This is a new list item
                # Check first item for the start index
                if not items and self.TAG == 'ol':
                    # Detect the integer value of first list item
                    INTEGER_RE = re.compile(r'(\d+)')
                    self.STARTSWITH = INTEGER_RE.match(m.group(1)).group()
                # Append to the list
                items.append(m.group(3))
            elif self.INDENT_RE.match(line):
                # This is an indented (possibly nested) item.
                if items[-1].startswith(' '*self.tab_length):
                    # Previous item was indented. Append to that item.
                    items[-1] = '%s\n%s' % (items[-1], line)
                else:
                    items.append(line)
            else:
                # This is another line of previous item. Append to that item.
                items[-1] = '%s\n%s' % (items[-1], line)
        return items


class UListProcessor(OListProcessor):
    """ Process unordered list blocks. """

    TAG = 'ul'

    def __init__(self, parser, cfg):
        super(UListProcessor, self).__init__(parser, cfg)
        # Detect an item (``1. item``). ``group(1)`` contains contents of item.
        self.RE = re.compile(r'^[ ]{0,%d}[*+-][ ]+(.*)' % (self.tab_length - 1))



class BlockQuoteProcessor(BlockProcessor):
    
    RE = re.compile(r'(^|\n)[ ]{0,3}>[ ]?(.*)')

    def __init__(self, parser, cfg):
        self.cfg = cfg
        super(BlockQuoteProcessor, self).__init__(parser)

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        if m:
            before = block[:m.start()]  # Lines before blockquote
            # Pass lines before blockquote in recursively for parsing forst.
            self.parser.parseBlocks(parent, [before])
            # Remove ``> `` from beginning of each line.
            block = '\n'.join(
                [self.clean(line) for line in block[m.start():].split('\n')]
            )
        sibling = self.lastChild(parent)
        if sibling is not None and sibling.tag == "blockquote":
            # Previous block was a blockquote so set that as this blocks parent
            quote = sibling
        else:
            # This is a new blockquote. Create a new parent element.
            ## michael.wu ---
            # quote = util.etree.SubElement(parent, 'blockquote')
            block_cfg = self.cfg.get("ref")
            quote = helper.add_subelement_list(parent, block_cfg, ['p'])
            quote.text = block
            ## michael.wu +++
        # Recursively parse block with blockquote as parent.
        # change parser state so blockquotes embedded in lists use p tags
        self.parser.state.set('blockquote')
        self.parser.parseChunk(quote, block)
        self.parser.state.reset()

    def clean(self, line):
        """ Remove ``>`` from beginning of a line. """
        m = self.RE.match(line)
        if line.strip() == ">":
            return ""
        elif m:
            return m.group(2)
        else:
            return line

class HashHeaderProcessor(BlockProcessor):
    """ Process Hash Headers. """

    # header 1 ~ 6 (index 1 for place holder, index 0 to store [2] current number)
    counter = [1, 0, 0, 1, 1, 1, 1]

    # Detect a header at start of any line in block
    RE = re.compile(r'(^|\n)(?P<level>#{1,6})(?P<header>.*?)#*(\n|$)')

    def __init__(self, parser, cfg):
        self.cfg = cfg
        self.h1_cfg = cfg.get("h1")
        self.h2_cfg = cfg.get("h2")
        self.h3_cfg = cfg.get("h3")
        super(HashHeaderProcessor, self).__init__(parser)

    def test(self, parent, block):
        return bool(self.RE.search(block))

    def set_weixin_layout(self, parent, num, text) :
        if num == 2:
            pre_num = self.h2_cfg.get("pre-num")
            br = self.h2_cfg.get("br")
            attrs = self.h2_cfg.get("attrs")
            title = self.h2_cfg.get("title")

            ## pre number:
            span = helper.add_subelement_list(parent, pre_num, ['p', 'strong', 'em', 'span'])
            # we count it as the index number
            self.counter[2] += 1
            span.text = str(self.counter[2])
            ## br
            p2 = util.etree.SubElement(parent, 'p')
            util.etree.SubElement(p2, 'br')
            p2_attrs = br.get('p')
            helper.set_tag_attrs(p2, p2_attrs)
            ## h2
            h2 = util.etree.SubElement(parent, 'h2')
            h2.text = "  "
            helper.set_tag_attrs(h2, attrs)
            ## title
            span = helper.add_subelement_list(parent, title, ['p', 'strong', 'span'])
            span.text = text
            
        elif num == 3:
            pre_num = self.h3_cfg.get("pre-num")
            br = self.h3_cfg.get("br")
            attrs = self.h3_cfg.get("attrs")
            title = self.h3_cfg.get("title")

            ## pre number:
            span2 = helper.add_subelement_list(parent, pre_num, ['p', 'span1', 'strong', 'em', 'span2'])
            ## count the index number
            if self.counter[2] == self.counter[0] + 1 :
                self.counter[3] = 1 # reset it, now count 
                self.counter[0] = self.counter[2] # using [0] to save its parent's index
            span2.text = str(self.counter[2]) + "." + str(self.counter[3])
            if self.counter[2] == self.counter[0] :
                self.counter[3] += 1

            ## br
            p2 = util.etree.SubElement(parent, 'p')
            util.etree.SubElement(p2, 'br')
            p2_attrs = br.get('p')
            helper.set_tag_attrs(p2, p2_attrs)
            ## h3
            h3 = util.etree.SubElement(parent, 'h3')
            h3.text = "  "
            helper.set_tag_attrs(h3, attrs)
            ## title
            span2 = helper.add_subelement_list(parent, title, ['p', 'strong1', 'span1', 'strong2', 'span2'])
            span2.text = text
            
        else :
            logger.warn("We do not handle header: %d, using default process" % num)
            h = util.etree.SubElement(parent, 'h%d' % num)
            h.text = text
            

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        if m:
            before = block[:m.start()]  # All lines before header
            after = block[m.end():]     # All lines after header
            if before:
                # As the header was not the first line of the block and the
                # lines before the header must be parsed first,
                # recursively parse this lines as a block.
                self.parser.parseBlocks(parent, [before])
            ## michael.wu added ---
            # Create header using named groups from RE
            # h = util.etree.SubElement(parent, 'h%d' % len(m.group('level')))
            # h.text = m.group('header').strip()
            num = len(m.group('level'))
            text = m.group('header').strip()
            self.set_weixin_layout(parent, num, text)
            ## michael.wu added +++

            if after:
                # Insert remaining lines as first block for future parsing.
                blocks.insert(0, after)
        else:  # pragma: no cover
            # This should never happen, but just in case...
            logger.warn("We've got a problem header: %r" % block)

class ParagraphProcessor(BlockProcessor):
    """ Process Paragraph blocks. """

    def __init__(self, parser, cfg):
        self.cfg = cfg
        super(ParagraphProcessor, self).__init__(parser)

    def test(self, parent, block):
        return True

    def run(self, parent, blocks):
        block = blocks.pop(0)
        if block.strip():
            # Not a blank block. Add to parent, otherwise throw it away.
            if self.parser.state.isstate('list'):
                # The parent is a tight-list.
                #
                # Check for any children. This will likely only happen in a
                # tight-list when a header isn't followed by a blank line.
                # For example:
                #
                #     * # Header
                #     Line 2 of list item - not part of header.
                sibling = self.lastChild(parent)
                if sibling is not None:
                    # Insetrt after sibling.
                    if sibling.tail:
                        sibling.tail = '%s\n%s' % (sibling.tail, block)
                    else:
                        sibling.tail = '\n%s' % block
                else:
                    # Append to parent.text
                    if parent.text:
                        parent.text = '%s\n%s' % (parent.text, block)
                    else:
                        parent.text = block.lstrip()
            else:
                # Create a regular paragraph
                # michael.wu changed ---
                # p = util.etree.SubElement(parent, 'p')
                # p.text = block.lstrip()
                span = helper.add_subelement_list(parent, self.cfg, ['p', 'span'])
                span.text = block.lstrip()
                # michael.wu changed +++
