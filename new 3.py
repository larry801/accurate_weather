import csv
from io import open
f=open("region.csv", encoding='utf-8')
aa = csv.DictReader(f,
                        fieldnames=["code", "name", "parent_code", "lng", "lat", "created_at", "updated_at"],
                        delimiter=','
                        )
o={}
for rows in aa:
    o[rows["code"]] = {"lng": rows["lng"][2:-1], "lat": rows["lat"][2:-1], "name": rows["name"][2:-1]}

print(len(o))
b=o["34"]
f.close()
f=open("region.json",'w', encoding='utf-8')
import json
json.dump(o,f,ensure_ascii=False)
f.close()
