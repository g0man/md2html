import os
from markdown.postprocessors import Postprocessor

class HeaderPostprocessor(Postprocessor):

    def __init__(self, cfg, *args, **kwargs):
        self.cfg = cfg
        super(HeaderPostprocessor, self).__init__(*args, **kwargs)

    def run(self, root):
        header = os.path.join("config", self.cfg.get("header"))
        with open(header, "r") as f :
            reading_minutes = self.cfg.get('READING_MINUTES')
            print("reading minutes: %d" % reading_minutes)
            if reading_minutes < 1 :
                reading_minutes = 1
            data = f.read().replace('READING_MINUTES', str(reading_minutes))
            root = data + root
            f.close()

        return root

class FooterPostprocessor(Postprocessor):

    def __init__(self, cfg, *args, **kwargs):
        self.cfg = cfg
        super(FooterPostprocessor, self).__init__(*args, **kwargs)

    def run(self, root):
        
        filename = self.cfg.get("footer")
        footer = os.path.join("config", filename)
        with open(footer, "r") as f :
            root = root + f.read() 
            f.close()
        return root
