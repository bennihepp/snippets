import gdata.photos.service
import gdata.media
import gdata.geo

email = 'benjamin.hepp@gmail.com'
password = ''

gd_client = gdata.photos.service.PhotosService()
gd_client.email = email
gd_client.password = password
gd_client.source = 'photos'
gd_client.ProgrammaticLogin()

username = 'default'
albums = gd_client.GetUserFeed(user=username)
for album in albums.entry:
    print 'title: %s, number of photos: %s, id: %s' % (album.title.text,
            album.numphotos.text, album.gphoto_id.text)
album = albums.entry[0]

photos = gd_client.GetFeed(
    '/data/feed/api/user/%s/albumid/%s?kind=photo' % (
        username, album.gphoto_id.text))
for photo in photos.entry:
    print 'Photo title:', photo.title.text

print 'AlbumID:', photo.albumid.text
print 'PhotoID:', photo.gphoto_id.text
if photo.exif.make and photo.exif.model:
    camera = '%s %s' % (photo.exif.make.text, photo.exif.model.text)
else:
    camera = 'unknown'
print 'Camera:', camera
print 'Content URL:', photo.content.src
print 'First Thumbnail:', photo.media.thumbnail[0].url

