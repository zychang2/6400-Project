import requests
import json
import argparse

def apiReguests(url, params):
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        return -1
    else:
        print("Request was successful!")
    return response.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="program to make api requests for flight data")
    parser.add_argument("-i", type=str, help="Input file name", required=True)
    parser.add_argument("-j", type=str, help="json file name to log data", required=True)
    args = parser.parse_args()
    url = "https://aviation-edge.com/v2/public/flightsHistory?key=9d3d73-f61189&"
    with open(args.i, 'r') as file, open(args.j, "w") as file2:
        for line in file:
            param = {
                "code": line.strip(),
                "type" : "departure",
                "date_from": "2024-11-03",
                "date_to": "2024-11-09"
            }
            response = apiReguests(url, params=param)
            if (response != -1):
                json.dump(response, file2, indent=4)  


