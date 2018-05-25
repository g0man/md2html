import json
import logging

from markdown.extensions import Extension

from .knb_blockprocessor import (BlockQuoteProcessor, HashHeaderProcessor,
                                 OListProcessor, ParagraphProcessor,
                                 UListProcessor)
from .mw_inlinepatterns import ImagePattern
from .post_processor import FooterPostprocessor, HeaderPostprocessor
from .pre_processor import CalcReadingTimePreprocessor

logger = logging.getLogger('weixin/extension')


NOBRACKET = r'[^\]\[]*'
BRK = (
    r'\[(' +
    (NOBRACKET + r'(\[')*6 +
    (NOBRACKET + r'\])*')*6 +
    NOBRACKET + r')\]'
)
# ![alttxt](http://x.com/) or ![alttxt](<http://x.com/>)
IMAGE_LINK_RE = r'\!' + BRK + r'\s*\(\s*(<.*?>|([^"\)\s]+\s*"[^"]*"|[^\)\s]*))\s*\)'

class WeixinExtension(Extension):
    
    def __init__(self, *args, **kwargs):
        # Define config options and defaults
        # data = {}
        # with open("config/weixin.json", "r") as f:
        #     data = json.load(f)
        #     f.close()

        self.config = {
            'wxcfg': [{}]
        }
        # Call the parent class's __init__ method to configure options
        super(WeixinExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):

        cfg = self.getConfig('wxcfg')
        # print("cfg:  %s" % cfg)
        if cfg :
            # md.preprocessors.add('readtime', CalcReadingTimePreprocessor(cfg), "<normalize_whitespace") 
            md.postprocessors.add('header', HeaderPostprocessor(cfg), ">unescape") 
            md.postprocessors.add('payqrcode', FooterPostprocessor(cfg), ">header") 

            md.parser.blockprocessors['paragraph'] = ParagraphProcessor(md.parser, cfg)
            md.parser.blockprocessors['olist'] = OListProcessor(md.parser, cfg)
            md.parser.blockprocessors['ulist'] = UListProcessor(md.parser, cfg)
            md.parser.blockprocessors['quote'] = BlockQuoteProcessor(md.parser, cfg)
            md.parser.blockprocessors['hashheader'] = HashHeaderProcessor(md.parser, cfg)
            md.inlinePatterns["image_link"] = ImagePattern(IMAGE_LINK_RE, md, cfg)
        else :
            logger.warn("failed to get 'wxcfg' settings, do nothing.") 

def makeExtension(configs={}):
    return WeixinExtension(configs=configs)
