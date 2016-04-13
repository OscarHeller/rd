from base import BaseHandler
import os, uuid

# not the best way of doing it, probably? but who can say!
root = os.path.dirname(__file__).replace('handlers', '')

class MediaHandler(BaseHandler):
  def get(self):
    self.validateInternalPageAccess()

    images = [image for image in self.get_images()]
    user_id = self.get_current_user()

    self.render('media.html', images=images)

  def post(self):
    user_id = self.get_current_user()
    if user_id:
      file1 = self.request.files['filearg'][0]
      original_fname = file1['filename']

      print os.getcwd()
      output_file = open("web/static/media/assets/" + str(original_fname), 'wb')
      output_file.write(file1['body'])

      response = "Success, file " + original_fname + " is uploaded."
      self.add_image({'filename': original_fname})
    else:
      self.render('error.html')
