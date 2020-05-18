import requests
import pandas
import json
import os
from bs4 import BeautifulSoup

regions = {
    "københavn": "0",
    "sjælland": "1",
    "bornholm": "2",
    "lolland-falster": "3",
    "fyn": "4",
    "østjylland": "5",
    "nordjylland": "6",
    "vestjylland": "7",
    "sydjylland": "8",
    "andet": "9",
    "udland": "60",
    "danmark": "10"
}

genders = {
    "female": "s0",
    "male": "s1",
    "all": "s2"
}

types = {
    "first_names": "f",
    "middle_names": "m",
    "last_names": "l"
}

def create_url(region, gender, t):
    return f"http://www.danskernesnavne.navneforskning.ku.dk/Topnavne/Topnavn_reg{region}_{gender}_{t}.asp"

def fetch(url):
    print(url)
    r = requests.get(url)
    print(r.status_code)
    return r.text

data = {}

for gender_k, gender_v in genders.items():
    data[gender_k] = {}
    for type_k, type_v in types.items():
        data[gender_k][type_k] = {}
        for region_k, region_v in regions.items():
            data[gender_k][type_k][region_k] = {}
            url = create_url(region_v, gender_v, type_v)
            html = fetch(url)
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table')
            for tr in table.findAll('tr')[1:-1]:
                tds = tr.findAll('td')
                count = tds[1].text
                names = tds[2].text.split(',')
                for name in names:
                    data[gender_k][type_k][region_k][name] = count

def empty(name):
    r = {}
    r['name'] = name
    for region_k, _ in regions.items():
        r["count_" + region_k] = 0
    
    return r

def fetch():

    if not os.path.exists('csv'):
        os.mkdir('csv')
    if not os.path.exists('json'):
        os.mkdir('json')

    for gender_k, type_data in data.items():
        for type_k, region_data in type_data.items():
            df_data = {}
            for region_k, name_data in region_data.items():
                for name, count in name_data.items():
                    if df_data.get(name, None) is None:
                        df_data[name] = empty(name)

                    df_data[name]["count_" + region_k] = count

            arr = [i for i in df_data.values()]
            arr.sort(key = lambda x: int(x["count_danmark"]), reverse=True)

            # csv
            df = pandas.DataFrame.from_records(arr)
            csv_file_name = f"csv/{gender_k}_{type_k}.csv"
            df.to_csv(csv_file_name, index=False)
            print(csv_file_name)

            # json
            json_file_name = f"json/{gender_k}_{type_k}.json"
            with open(json_file_name,"w") as f:
                f.write(json.dumps(arr, ensure_ascii=False, indent=4))
                print(json_file_name)

if __name__ == '__main__':
    fetch()