import csv
from datetime import datetime

with open("airport_routes.csv","r",encoding="utf-8") as ogCsv, open("new.csv","w",newline="",encoding="utf-8") as newCsv:
    csvWriter = csv.writer(newCsv)
    csvReader = csv.reader(ogCsv)
    header = next(csvReader)
    csvWriter.writerow(header)
    for row in csvReader:
        time_obj = datetime.strptime(row[9], "%H:%M:%S")
        hours = time_obj.hour
        minutes = time_obj.minute
        seconds = time_obj.second
        total_minutes = hours * 60 + minutes + seconds // 60
        row[9] = total_minutes
        csvWriter.writerow(row)