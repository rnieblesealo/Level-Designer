"""
Transforms comma and equal string data into a key-value pair dict and vice-versa.
"""

def csv_dict(properties):
    # Adds a property/properties to this TileInfo
    dict = {}
    data = properties.replace(' ', '').split(',') # Remove whitespace & separate by commas
    for x in data:
        info = x.split(',')
        for i in info:
            if '=' in i:
                pair = i.split('=')
                dict[pair[0]] = pair[1]
            else:
                dict[i] = '1'
    return dict

def dict_csv(dict):
    data = ''
    for key, value in dict.items():
        data += '{K}={V},'.format(K=key, V=value)
    data = data[:-1] # Remove last char which will be a comma, not sure how splicing works here
    return data

sample = csv_dict('col=0, div=1')
print(dict_csv({}))