from model import Model

from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import transaction

storage = FileStorage('DB.fs')
db = DB(storage)
connection = db.open()
root = connection.root()

root['model-1'] = Model('abc')
root['model-2'] = Model('xyz')

transaction.commit()
print root.keys()

