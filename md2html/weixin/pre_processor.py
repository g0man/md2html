from markdown.preprocessors import Preprocessor


class CalcReadingTimePreprocessor(Preprocessor):
    
    def __init__(self, cfg, *args, **kwargs):
        self.cfg = cfg
        super(CalcReadingTimePreprocessor, self).__init__(*args, **kwargs)

    def run(self, root):
        word_count = len(root)
        print("word count: %d" % word_count)
        self.cfg['READING_MINUTES'] = int(word_count/700)
        return root