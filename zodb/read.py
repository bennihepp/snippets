from model import Model

from ZODB.FileStorage import FileStorage
from ZODB.DB import DB

storage = FileStorage('DB.fs')
db = DB(storage)
connection = db.open()
root = connection.root()

print root.keys()
m1 = root['model-1']
print m1.x
print m1.private()

m2 = root['model-2']
print m2.x
print m2.private()

