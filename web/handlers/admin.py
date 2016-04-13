import functools
from flash import Flash

def administrator(method):
    """Decorate with this method to restrict to site admins."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_admin():
            if self.request.method == "GET":

                flash = Flash('Access denied.', css_class='alert-danger')
                self.set_flash(flash, 'validation')

                self.redirect(self.get_argument('next', '/'))
                return
            raise tornado.web.HTTPError(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper