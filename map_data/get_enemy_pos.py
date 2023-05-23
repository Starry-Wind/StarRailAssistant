import json
# from jsonpath_ng import parse
import pandas as pd
# class Enemy():
#   self
class MapData():
    def __init__(self):
        self.point_folder = 'point/'
        self.info_folder = 'info/'
        self.get_map_list()
        self.get_data_collection()
        self.get_info_collection()
        self.get_map_info()
        self.load_enemy_labels()
        self.get_enemy_info()

    def get_map_list(self):
        with open('tree.json', "r", encoding="utf-8") as j:
            tree = json.load(j)
        map_list = []
        for map_d in tree['tree']:
            for children in map_d['children']:
                map_list.append(children['id'])     
        self.map_list = map_list

    def get_data_collection(self):
        self.data_collection = {}
        for map_id in self.map_list:
            with open(f'{self.point_folder}{map_id}.json', "r", encoding="utf-8") as j:
                json_data = json.load(j)    
            self.data_collection[map_id] = json_data

    def get_info_collection(self):
        self.info_collection = {}
        for map_id in self.map_list:
            with open(f'{self.info_folder}{map_id}.json', "r", encoding="utf-8") as j:
                json_data = json.load(j)    
            self.info_collection[map_id] = json_data

    def get_map_info(self):
        map_info = {}
        for map_id, more_info in self.info_collection.items():
            detail =json.loads(more_info['info']['detail'])
            map_info[map_id] = {
                'name' : more_info['info']['name'],
                'origin': detail['origin'],
                'size': detail['total_size'],
            } 
        self.map_info = map_info


    def get_all_labels(self, save=False):
        labels = {}
        for data in self.data_collection.values():
            for label_data in data['label_list']:
                lid = label_data['id']
                lname = label_data['name']
                if lid not in labels:
                    labels[lid] = lname
        self.labels = dict(sorted(labels.items(), key=lambda x:x[0]))

        if save:
            with open(f'labels.json', "w", encoding="utf-8") as j:
                json.dump(self.labels , j, indent=4, ensure_ascii=False)

    def load_enemy_labels(self):
        with open(f'enemy_labels.json', "r", encoding="utf-8") as j:
            self.enemy_labels = json.load(j)



    def get_enemy_info(self, save=0):
        enemy_info = []
        for map_id, data in self.data_collection.items():
            origin = self.map_info[map_id]['origin']
            map_name = self.map_info[map_id]['name']
            for point_data in data['point_list']:  
                label_id  = str(point_data['label_id'])
                # print(label_id)
                if label_id in self.enemy_labels.keys():
                    enemy_name = self.enemy_labels[label_id]
                else:
                    continue
                mhy_x = point_data['y_pos']
                mhy_y = point_data['x_pos']
                x = 2* (mhy_y + origin[0]) 
                y = 2* (mhy_x + origin[1])
                enemy_info.append({
                    'id': int(point_data['id']),
                    'name': enemy_name,
                    'map_id': int(map_id),
                    'map_name': map_name,
                    'x': int(x),
                    'y': int(y),
                    'mhy_x': int(mhy_x),
                    'mhy_y': int(mhy_y)
                })

        self.enemy_info = enemy_info
        if save:
            with open(f'enemy_info.json', "w", encoding="utf-8") as j:
                json.dump(self.enemy_info, j, indent=4, ensure_ascii=False)  

            df = pd.DataFrame(self.enemy_info)
            df.to_excel('enemy_info.xlsx', index=False)




md = MapData()
# md.get_all_labels(save=True)
md.load_enemy_labels()
md.get_enemy_info(1)
md.get_map_info()
# print(md.enemy_labels)
# print(md.map_info[62])
print(md.enemy_info)


# map_id = '62'
# with open(f'point/{map_id}.json', "r", encoding="utf-8") as j:

#   json_data = json.load(j)
#   print(json_data['point_list'][0])

