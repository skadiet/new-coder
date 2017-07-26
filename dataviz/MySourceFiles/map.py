import geojson
import parse as p

def create_map(data_file):
    geo_map = {'type': 'FeatureCollection'}
    item_list = []
    for index, line in enumerate(data_file):
        if line['X']=='0' or line['Y']=='0':
            continue
        data = {}
        data['type']= 'Feature'
        data['id'] = index
        data['properties'] = {'title': line['Category'],
                              'description': line['Descript'],
                              'date': line['Date']}
        data['geometry'] = {'type':'Point', 'coordinates': (line['X'], line['Y'])}

        item_list.append(data)

    for point in item_list:
        geo_map.setdefault('features', []).append(point)

    with open('file_sf.geojson', 'w') as f:
        f.write(geojson.dumps(geo_map))

def main():
    data = p.parse(p.MY_FILE, ",")
    return create_map(data)

if __name__ == '__main__':
    main()
