import pymongo
import xlwt

client = pymongo.MongoClient('localhost', 27017)
db = client['shanghai']
count=db['shanghai'].find()
workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet(u'sheet1', cell_overwrite_ok=True)

for i, d in enumerate(count):
    j = 0
    del d["_id"]
    for key, value in d.items():
        try:
            worksheet.write(i, j, label=value)
        except Exception as e:
            print(e)
            pass
        j += 1

workbook.save("meituan.xls")


