"""
INLINE PATTERNS
=============================================================================

Inline patterns such as *emphasis* are handled by means of auxiliary
objects, one per pattern.  Pattern objects must be instances of classes
that extend markdown.Pattern.  Each pattern object uses a single regular
expression and needs support the following methods:

    pattern.getCompiledRegExp() # returns a regular expression

    pattern.handleMatch(m) # takes a match object and returns
                           # an ElementTree element or just plain text

All of python markdown's built-in patterns subclass from Pattern,
but you can add additional patterns that don't.

Also note that all the regular expressions used by inline must
capture the whole block.  For this reason, they all start with
'^(.*)' and end with '(.*)!'.  In case with built-in expression
Pattern takes care of adding the "^(.*)" and "(.*)!".

Finally, the order in which regular expressions are applied is very
important - e.g. if we first replace http://.../ links with <a> tags
and _then_ try to replace inline html, we would end up with a mess.
So, we apply the expressions in the following order:

* escape and backticks have to go before everything else, so
  that we can preempt any markdown patterns by escaping them.

* then we handle auto-links (must be done before inline html)

* then we handle inline HTML.  At this point we will simply
  replace all inline HTML strings with a placeholder and add
  the actual HTML to a hash.

* then inline images (must be done before links)

* then bracketed links, first regular then reference-style

* finally we apply strong and emphasis
"""

## we get base code from markdown.inlinepattern


import re

from markdown import util
from markdown.inlinepatterns import LinkPattern, dequote, handleAttributes

# def build_inlinepatterns(md_instance, **kwargs):
#     """ Build the default set of inline patterns for Markdown. """
#     inlinePatterns["image_link"] = ImagePattern(IMAGE_LINK_RE, md_instance)

# NOBRACKET = r'[^\]\[]*'
# BRK = (
#     r'\[(' +
#     (NOBRACKET + r'(\[')*6 +
#     (NOBRACKET + r'\])*')*6 +
#     NOBRACKET + r')\]'
# )
# # ![alttxt](http://x.com/) or ![alttxt](<http://x.com/>)
# IMAGE_LINK_RE = r'\!' + BRK + r'\s*\(\s*(<.*?>|([^"\)\s]+\s*"[^"]*"|[^\)\s]*))\s*\)'

# def dequote(string):
#     """Remove quotes from around a string."""
#     if ((string.startswith('"') and string.endswith('"')) or
#        (string.startswith("'") and string.endswith("'"))):
#         return string[1:-1]
#     else:
#         return string


# ATTR_RE = re.compile(r"\{@([^\}]*)=([^\}]*)}")  # {@id=123}


# def handleAttributes(text, parent):
#     """Set values of an element based on attribute definitions ({@id=123})."""
#     def attributeCallback(match):
#         parent.set(match.group(1), match.group(2).replace('\n', ' '))
#     return ATTR_RE.sub(attributeCallback, text)


class ImagePattern(LinkPattern):
    
    def __init__(self, pattern, markdown_instance, cfg):
        super(ImagePattern, self).__init__(pattern, markdown_instance)
        self.cfg = cfg
    
    """ Return a img element from the given match. """
    def handleMatch(self, m):
        el = util.etree.Element("img")

        print("handle image tag ============")
        src_parts = m.group(9).split()
        if src_parts:
            src = src_parts[0]
            if src[0] == "<" and src[-1] == ">":
                src = src[1:-1]
            el.set('src', self.sanitize_url(self.unescape(src)))

            # michael.wu add +++
            img_cfg = self.cfg.get("img")
            for k, v in img_cfg.items() :
                el.set(k, v)
            # michael.wu add ---
        else:
            el.set('src', "")
        if len(src_parts) > 1:
            el.set('title', dequote(self.unescape(" ".join(src_parts[1:]))))

        if self.markdown.enable_attributes:
            truealt = handleAttributes(m.group(2), el)
        else:
            truealt = m.group(2)

        el.set('alt', self.unescape(truealt))
        return el
