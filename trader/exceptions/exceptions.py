class UnexpectedSymbolStatusException(Exception):
    def __init__(self, status):
        super().__init__()
        self.status = status

    def __str__(self):
        return f'UnexpectedSymbolStatusException(status={self.status})'    

class ChangeStatusTimeoutException(Exception):
    def __init__(self, status, duration):
        super().__init__()
        self.status = status
        self.duration = duration

    def __str__(self):
        return f'ChangeStatusTimeoutException(status={self.status}, duration={self.duration})'

class WrappingException(Exception):
    def __init__(self, parent_exception: Exception):
        super().__init__()
        self.parent_exception = parent_exception
        self.__cause__ = parent_exception

class SaveTradeException(WrappingException):

    def __str__(self):
        return f'SaveTradeException: {self.parent_exception}'

class UnconfirmedBuyException(WrappingException):

    def __str__(self):
        return f'UnconfirmedBuyException: {self.parent_exception}'
    
class SubmissionTimeoutException(WrappingException):
    def __init__(self, side, parent_exception):
        super().__init__(parent_exception)
        self.side = side

    def __str__(self):
        return f'SubmissionTimeoutException(side={self.side}): {self.parent_exception}'
    

class HandleRequestException(WrappingException):
    def __init__(self, request: dict, parent_exception):
        super().__init__(parent_exception)
        self.request = request

    def __str__(self):
        return f'Failed to handle request {self.request}: {self.parent_exception}'
    

class ExchangeInitializationException(WrappingException):

    def __str__(self):
        return f'Failed to initialize exchange: {self.parent_exception}'
    
class WalletInitializationException(WrappingException):

    def __str__(self):
        return f'Failed to initialize wallet: {self.parent_exception}'


class OrderSubmissionException(WrappingException):

     def __init__(self, side: str, parent_exception):
        super().__init__(parent_exception)
        self.side = side