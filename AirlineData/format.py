import json
import csv

airport = {}

with open("processed_airports.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)
    for entry in data:
        airport[entry["IATA code"]] = [entry["region_name"], entry["region_id"]]

with open("japan_codes_city.csv","r",encoding="utf-8") as ogCsv, open("japan_city.csv","w",newline="",encoding="utf-8") as newCsv:
    csvWriter = csv.writer(newCsv)
    csvReader = csv.reader(ogCsv)
    header = next(csvReader)
    csvWriter.writerow(header)
    for row in csvReader:
        row[2] = airport.get(row[0])[0]
        row.append(airport.get(row[0])[1])
        csvWriter.writerow(row)
        
