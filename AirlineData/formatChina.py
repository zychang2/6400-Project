import csv

airport = {}

with open("processed_routes.csv", "r", encoding="utf-8") as csv_file:
    csvReader = csv.reader(csv_file)
    for row in csvReader:
        airport[row[2]] = row[1]

with open("airport_city.csv","r",encoding="utf-8") as ogCsv, open("china_city.csv","w",newline="",encoding="utf-8") as newCsv:
    csvWriter = csv.writer(newCsv)
    csvReader = csv.reader(ogCsv)
    header = next(csvReader)
    csvWriter.writerow(header)
    for row in csvReader:
        if (airport.__contains__(row[2])):
            row.append(airport.get(row[2]))
        else:
            print(row[2])
            row.append("NULL")
        csvWriter.writerow(row)
        
