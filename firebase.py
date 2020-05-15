import firebase_admin
from firebase_admin import credentials, firestore, storage

import pyrebase

fname = "path of firebase jason"
cred=credentials.Certificate(r'‪C:/HC/parking.json'.replace('\u202a',""))
firebase_admin.initialize_app(cred,{
    'storageBucket': ''
})

config = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "",
    "measurementId": ""
}
try:
    f = [open('‪C:/HC/afterCrop/ocr%d.text'.replace('\u202a',"")%i,'r')for i in range(1,4)]
    read = []
    for i in range(0,len(f)):
        read.append(f[i].read())
finally:
    for fh in f:
        fh.close()
ocr_txt = ""
for i in range(0,len(read)):
    if(read[i]=="parknum is not found"):
        ocr_txt="null"
    else:
        ocr_txt=read[i]
        break

print(ocr_txt)

firebase = pyrebase.initialize_app(config)
db = firebase.database()
#db.child("name").push({"parknum":ocr_txt})
#db.child("name").remove()
#db = firestore.client()
bucket = storage.bucket()
blobs=[]
for i in range(0,3):
    blobs.append(bucket.blob('test{}'.format(i+1)))
for i in range(0,3):
    outfile = '‪C:\\HC\\imgList\\test_{}.jpg'.format(i+1).replace('\u202a',"")
    with open(outfile,'rb') as my_file:
        blobs[i].upload_from_file(my_file)