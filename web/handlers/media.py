from base import BaseHandler
import os, uuid

# not the best way of doing it, probably? but who can say!
root = os.path.dirname(__file__).replace('handlers', '')
__UPLOADS__ = root + "/static/media/backgrounds/"

class MediaHandler(BaseHandler):
  def get(self):
    user_id = self.get_current_user()
    if user_id:
        self.render('media.html')
    else:
        self.render('error.html')

  def post(self):
    fileinfo = self.request.files['filearg'][0]
    print "fileinfo is", fileinfo
    fname = fileinfo['filename']
    extn = os.path.splitext(fname)[1]
    cname = str(uuid.uuid4()) + extn
    fh = open(__UPLOADS__ + str(fname), 'w')
    fh.write(fileinfo['body'])
    self.finish(fname + " is uploaded!! Check %s folder" %__UPLOADS__)