from pygame import image, transform
import os

dirname = os.path.split(os.path.abspath(__file__))[0]
os.chdir(dirname)

def load_img(path):
    img = image.load(path)
    img = transform.scale(img, (60, 60))
    return img


class Setting:

    coors_plate = [[1010, 2010, 3010, 4010, 5000, 4020, 3020, 2020, 1020],
                   [0000, 0000, 0000, 0000, 0000, 0000, 0000, 0000, 0000],
                   [0000, 6010, 0000, 0000, 0000, 0000, 0000, 6020, 0000],
                   [7010, 0000, 7020, 0000, 7030, 0000, 7040, 0000, 7050],
                   [0000, 0000, 0000, 0000, 0000, 0000, 0000, 0000, 0000],
                   #                    楚河      汉界                  #
                   [0000, 0000, 0000, 0000, 0000, 0000, 0000, 0000, 0000],
                   [7110, 0000, 7120, 0000, 7130, 0000, 7140, 0000, 7150],
                   [0000, 6110, 0000, 0000, 0000, 0000, 0000, 6120, 0000],
                   [0000, 0000, 0000, 0000, 0000, 0000, 0000, 0000, 0000],
                   [1110, 2110, 3110, 4110, 5100, 4120, 3120, 2120, 1120]]

    coors_chess = {'1011': 'ju', '1021': 'ju', '1111': 'ju', '1121': 'ju',
                   '2011': 'ma', '2021': 'ma', '2111': 'ma', '2121': 'ma',
                   '3011': 'xiang', '3021': 'xiang', '3111': 'xiang', '3121': 'xiang',
                   '4011': 'shi', '4021': 'shi', '4111': 'shi', '4121': 'shi',
                   '5001': 'shuai', '5101': 'jiang', '6011': 'pao', '6021': 'pao', '6111': 'pao', '6121': 'pao',
                   '7011': 'bing', '7021': 'bing', '7031': 'bing', '7041': 'bing', '7051': 'bing',
                   '7111': 'bing', '7121': 'bing', '7131': 'bing', '7141': 'bing', '7151': 'bing'}

    legal_move = {'ju': [],
                  'ma': [],
                  'xiang': [],
                  'shi': [],
                  'jiang': [],
                  'shuai': [],
                  'pao': [],
                  'bing': []
                  }

    img = {
        'red_ju': load_img('red/ju.png'),
        'red_ma': load_img('red/ma.png'),
        'red_xiang': load_img('red/xiang.png'),
        'red_shi': load_img('red/shi.png'),
        'red_shuai': load_img('red/shuai.png'),
        'red_pao': load_img('red/pao.png'),
        'red_bing': load_img('red/bing.png'),
        'black_ju': load_img('black/ju.png'),
        'black_ma': load_img('black/ma.png'),
        'black_xiang': load_img('black/xiang.png'),
        'black_shi': load_img('black/shi.png'),
        'black_jiang': load_img('black/jiang.png'),
        'black_pao': load_img('black/pao.png'),
        'black_bing': load_img('black/bing.png')
           }

    score = {
        10: 16,
        20: 8,
        30: 4,
        40: 3,
        50: 3,
        60: 8,
        70: 1,
        11: -16,
        21: -8,
        31: -4,
        41: -3,
        51: -3,
        61: -8,
        71: -1
            }

