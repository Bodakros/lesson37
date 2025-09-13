import colorama
from colorama import Fore, Style

colorama.init()


class DPrintBase:
    def __init__(self, prefix='', is_without_repeats=False):
        self.prefix = prefix
        self.is_without_repeats = is_without_repeats
        self.cache = ''


class DPrint(DPrintBase):
    log_filename = 'bot_log.log'

    def __init__(self, prefix='', is_without_repeats=False, base: DPrintBase | None = None):
        if base is not None:
            prefix = f'{base.prefix} [{prefix}]'
        else:
            prefix = f'[{prefix}]'

        super().__init__(prefix, is_without_repeats)

    def __call__(self, *args, color=Fore.WHITE, level='I'):
        """
        Regular information
        """
        txt = ' '.join(args)

        if self.is_without_repeats and txt == self.cache:
            return

        self.cache = txt

        text = (
                f'[{level}]' +
                f'{self.prefix} ' + txt
        )
        print(color + text + Style.RESET_ALL)
        with open(DPrint.log_filename, 'a', encoding='UTF8') as f:
            f.write(text + '\n')

    def error(self, text):
        """
        Critical error. Maybe a bug?
        """
        self(text, color=Fore.RED, level='E')

    def success(self, text):
        """
        Success of something
        """
        self(text, color=Fore.GREEN, level='O')

    def warn(self, text):
        """
        Warnings. Resolvable
        """
        self(text, color=Fore.YELLOW, level='W')

    def admin(self, text):
        """
        Admin information
        """
        self(text, color=Fore.CYAN, level='A')

    def rare(self, text):
        """
        Special rare information
        """
        self(text, color=Fore.MAGENTA, level='S')



