import csv
from datetime import datetime

# with open("airport_routes.csv","r",encoding="utf-8") as ogCsv, open("new.csv","w",newline="",encoding="utf-8") as newCsv:
#     csvWriter = csv.writer(newCsv)
#     csvReader = csv.reader(ogCsv)
#     header = next(csvReader)
#     csvWriter.writerow(header)
#     for row in csvReader:
#         time_obj = datetime.strptime(row[9], "%H:%M:%S")
#         hours = time_obj.hour
#         minutes = time_obj.minute
#         seconds = time_obj.second
#         total_minutes = hours * 60 + minutes + seconds // 60
#         row[9] = total_minutes
#         csvWriter.writerow(row)

with open("airport_routes.csv","r",encoding="utf-8") as ogCsv, open("new.csv","w",newline="",encoding="utf-8") as newCsv:
    csvWriter = csv.writer(newCsv)
    csvReader = csv.reader(ogCsv)
    header = next(csvReader)
    csvWriter.writerow(header)
    for row in csvReader:
        for i in [2, 5]:
            if row[i] == 'shaanxi':
                row[i] = 'shanxi'
                row[i - 1] = 1018
            elif row[i] == 'fuijan':
                row[i] = 'fujian'
                row[i - 1] = 1003
            elif row[i] == 'guangxi':
                row[i] = 'guangxizhuangzuzizhiqu'
                row[i - 1] = 1005
            
        csvWriter.writerow(row)