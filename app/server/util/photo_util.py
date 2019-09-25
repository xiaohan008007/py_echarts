from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from aip import AipOcr
import json

save_croped = True


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def croped(im, file_path, file_name, left, top, right, bottom):
    cropedIm = im.crop((left, top, right, bottom))
    # cropedIm = ImageEnhance.Color(cropedIm).enhance(2.0)
    # cropedIm = ImageEnhance.Brightness(cropedIm).enhance(0.9)
    # cropedIm = ImageEnhance.Contrast(cropedIm).enhance(4.0)
    # cropedIm = ImageEnhance.Sharpness(cropedIm).enhance(2.0)
    if save_croped:
        cropedIm.save(file_path + file_name)
    text = pytesseract.image_to_string(cropedIm, config='--psm 6 -c tessedit_char_whitelist=0123456789.,+-%',
                                       lang='eng')
    text = text.replace('\n\n', '\n')
    return text


def cut_column(im, file_path, file_name, left, top, right, bottom):
    text = croped(im, file_path, file_name, left, top, right, bottom)
    return str_to_arr(text)


def cut_3column(im, file_path, file_name, left, top, right, bottom):
    text = croped(im, file_path, file_name, left, top, right, bottom)
    return str_to_3arr(text)


def get_3column(times, im, file_path):
    croped_name = 'cropped.png'
    if times == 1:
        return cut_3column(im, file_path, croped_name, 650, 40, 1150, 610)
    else:
        g1 = cut_column(im, file_path, croped_name, 650, 40, 750, 610)
        g2 = cut_column(im, file_path, croped_name, 850, 40, 950, 610)
        g3 = cut_column(im, file_path, croped_name, 1050, 40, 1150, 610)
        return g1, g2, g3


def str_to_arr(text):
    arr = text.split('\n')
    return arr


def str_to_3arr(text):

    group = text.split('\n')
    g1 = []
    g2 = []
    g3 = []
    index = 1
    for g in group:
        g1.append(g)
        # if g.find('%') > -1:
        #     g2.append(g)
        #     index = 2
        # elif index == 2:
        #     g3.append(g)
    return g1, g2, g3

def parse_first_column_google(photo_type, im, local_path):
    if photo_type == '1':
        cut_right = 200
    elif photo_type == '2':
        cut_right = 300
    else:
        cut_right = 150
    cropedIm = im.crop((80, 40, cut_right, 610))
    # cropedIm.filter(ImageFilter.DETAIL)
    cropedIm = ImageEnhance.Brightness(cropedIm).enhance(0.9)
    cropedIm = ImageEnhance.Contrast(cropedIm).enhance(4.0)
    cropedIm = ImageEnhance.Sharpness(cropedIm).enhance(1.5)
    f_path = local_path + 'cropped.png'
    text = pytesseract.image_to_string(cropedIm, config='--psm 6 -c tessedit_char_whitelist=0123456789.,+-%',
                                       lang='chi_sim')
    return text



def parse_first_column(photo_type, client, im, local_path):
    if photo_type == '1':
        cut_right = 200
    elif photo_type == '2':
        cut_right = 300
    else:
        cut_right = 150
    cropedIm = im.crop((80, 40, cut_right, 610))
    # cropedIm.filter(ImageFilter.DETAIL)
    cropedIm = ImageEnhance.Brightness(cropedIm).enhance(0.9)
    cropedIm = ImageEnhance.Contrast(cropedIm).enhance(4.0)
    cropedIm = ImageEnhance.Sharpness(cropedIm).enhance(1.5)
    f_path = local_path + 'cropped.png'
    cropedIm.save(f_path)

    image = get_file_content(f_path)
    options = {}
    options["language_type"] = "CHN_ENG"
    # options["detect_direction"] = "true"
    # options["detect_language"] = "true"
    # options["probability"] = "true"
    options["language"] = "3"
    if photo_type == 3:
        # 高清
        jsons = client.basicAccurate(image, options)
    else:
        jsons = client.basicGeneral(image, options)
    # j_data = json.dumps(jsons)
    # print(j_data)
    items = jsons['words_result']
    g0 = []
    item_str = ""
    m = 1
    for item in items:
        if photo_type == '3':
            g0.append(item['words'])
        else:
            if m % 2 == 0:
                item_str += '(' + item['words'] + ")"
                g0.append(item_str)
                item_str = ""
            else:
                item_str = item['words']
        m += 1
    return g0

def parse_photo_cell(local_path, file_name):
    column = 1

    g1 = []
    g2 = []
    g3 = []
    im = Image.open(local_path + file_name)  # 打开图片
    for k in range(550, 1150, 200):
        for i in range(40, 620, 58):
            cropedIm = im.crop((k, i, k + 200, i + 58))
            # cropedIm.filter(ImageFilter.DETAIL)

            # cropedIm.save('/Users/ludanqing/python/qly_project/pyecharts/pyecharts/app/server/photo/cropped.png')
            text = pytesseract.image_to_string(cropedIm, lang='eng')
            if column == 1:
                g1.append(text)
            elif column == 2:
                g2.append(text)
            elif column == 3:
                g3.append(text)
            # str += text+"<br>"
        # str += "\n"
        column += 1

    return g1, g2, g3