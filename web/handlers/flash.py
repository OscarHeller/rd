class Flash(object):
    """
    A flash message along with optional (form) data.
    """

    def __init__(self, message, css_class='', data=None):
        """
        'message': A string.
        'data': Can be anything.
        """
        self.message = message
        self.data = data
        self.css_class = css_class
