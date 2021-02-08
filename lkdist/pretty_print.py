from contextlib import contextmanager


class Printer:
    
    def __init__(self, scrwidth=80):
        # scrwidth: 'screen width'. suggest 50|80(default)|120|100.
        self.indent = 0
        self.scrwidth = scrwidth
    
    @contextmanager
    def heading(self, text: str):
        """
        Args:
            text:
            
        Examples:
            Code:
                printer = Printer()
                with printer.heading('This is a heading'):
                    #        ^^^^^^^
                    printer.info('Test OK')
                    printer.info('You need to track the trouble')
            Prints:
                ================ [This is a heading] ================
                    Test OK
                    You need to track the trouble
        """
        text = f'[{text}]'
        assert len(text) <= self.scrwidth, \
            'Please keep the length of text({}) less than {} ' \
            'characters!'.format(len(text) - 2, self.scrwidth - 2)
        self.indent += 4
        delimeter = int((self.scrwidth - len(text)) / 2)
        delimeter = '=' * delimeter
        try:
            print(delimeter, text, delimeter)
            yield self
        finally:
            self.indent -= 4
    
    def info(self, *msg: str, status=None):
        """
        Args:
            status: (None|bool)
                None: No status info
                True: A successful status. It will be translated to '[succeed]'
                False: A failed status. It will be translated to '[failed]'
            *msg:
                Note: Please don't use \n here, it would affect the performance
                of `self._wrap_line`.
                
        Examples:
            Code:
                with printer.heading('HEADER'):
                    printer.info('Alpha', 'Beta', 'Gamma')
            Prints:
                ================ [HEADER] ================
                    Alpha
                    Beta
                    Gamma
            Code:
                with printer.heading('HEADER'):
                    printer.info('Alpha', 'Beta', 'Gamma', status=True)
            Prints:
                ================ [HEADER] ================
                    [succeed]
                        Alpha
                        Beta
                        Gamma
            Code:
                with printer.heading('HEADER'):
                    printer.info('Alpha', 'Beta', 'Gamma', status=False)
            Prints:
                ================ [HEADER] ================
                    [failed]
                        Alpha
                        Beta
                        Gamma
        """
        lspacing = ' ' * self.indent
        
        if isinstance(status, bool):
            print(lspacing + ('[succeed]' if status else '[failed]'))
            lspacing += lspacing
        
        for line in msg:
            print('\n'.join(self._wrap_line(line, lspacing=lspacing)))
        
        return status
    
    def ask(self, *msg):
        """
        
        Args:
            *msg:

        Examples:
            response = printer.ask('The configuration is not correct!',
                                   'Would you like me to repair it?')
        
        Returns:
            resp: bool. Input 'y' or 'Y' returns True, or anything else returns
                False
        """
        lspacing = ' ' * self.indent
        for line in msg[:-1]:
            print('\n'.join(self._wrap_line(line, lspacing=lspacing)))
        return input(lspacing + msg[-1] + ' (y/n): ').lower() == 'y'
    
    def _wrap_line(self, line, lspacing='    '):
        """ Ensure each line not exceeds 80 characters.
                                         ^^ depends on `self.scrwidth`
        
        Notes:
            - 暂不支持根据单词换行. 即换行处可能打破一个完整的单词
        
        Returns:
            (假设 lspacing 是四个空格, 下面为了方便看清, 我们用 · 来表示空格)
            (假设 line 是一个非常长的行 (超过 80 字符), line 的内容将如下所示)
            
            ····Now setup goes to the final step! We will help installing the ne
            ····cessary dependencies into your computer, they will be installed
            ····at the global Python site-packages (usually it can be found at "
            ····C:\\Program Files\\Python38").
        """
        step = self.scrwidth - len(lspacing)
        for i in range(0, len(line), step):
            yield lspacing + line[i: i + step]


printer = Printer()
