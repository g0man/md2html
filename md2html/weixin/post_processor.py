import os
from markdown.postprocessors import Postprocessor

def _get_snippet_filename(cfg, cmdkey, cmdpath, cfgkey):
    filename = cfg.get(cmdkey)
    if not filename :
        cfg_path = cfg.get(cmdpath)

        if cfg_path is None or cfg_path == '' :
            filename = cfg.get(cfgkey)
        else :
            filename = os.path.join(cfg_path, cfg.get(cfgkey))
    return filename

class HeaderPostprocessor(Postprocessor):

    def __init__(self, cfg, *args, **kwargs):
        self.cfg = cfg
        super(HeaderPostprocessor, self).__init__(*args, **kwargs)

    def run(self, root):
        filename = _get_snippet_filename(self.cfg, "__cmd_header_file__", "__cmd_cfg_path__", "header")
        with open(filename, "r") as f :
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
        
        filename = _get_snippet_filename(self.cfg, "__cmd_footer_file__", "__cmd_cfg_path__", "footer")

        with open(filename, "r") as f :
            root = root + f.read() 
            f.close()
        return root
