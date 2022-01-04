from flask import Flask, render_template,request
import os
import subprocess
import time
import requests
import json
#import adafruit_gps
#import RPi.GPIO as GPIO
import urllib.error
import urllib.parse
import urllib.request
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import io
import platform
import datetime
import shutil
import qrcode
app = Flask(__name__)

'''start of script functions'''

def inst_google():
    api_key = 'xxxx'

    return api_key

def get_time():
    return time.asctime(time.localtime(time.time()))

def get_datetime():
    time = datetime.datetime.now()
    year = time.strftime("%y")
    month = time.strftime("%m")
    day = time.strftime("%d")

    current_day_path = year + '-' + month + day + '-'

    return current_day_path

def get_google_maps_api(api_key, latitude, longitude):
    location = str(latitude) + ',' + str(longitude)

    degree = 0

    image_append = ''
    width_append = 0

    list_filenames = []
    image_paths = []

    for i in range(4):

        #google api call
        parameters = urllib.parse.urlencode({
            "size": '600x600',
            "location": location,
            "key": api_key,
            "heading": degree
            })

        url = f"https://maps.googleapis.com/maps/api/streetview?{parameters}"
        gmap_pic = urllib.request.urlopen(url)
        #print(url)
        #print("*********")
        image = Image.open(gmap_pic)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(r"arial.ttf", 26)

        #draw text on image
        draw.text((0,0), 'Latitude: ' + str(latitude) + '\nLongitude: ' + str(longitude) + '\n' + 'Rotation Degree: ' + str(degree) + '\n' + get_time(), (255,0,0), font=font)

        #create directory if it doesn't exist
        current_day_path = get_datetime()

        path = os.path.join(os.path.dirname(__file__), 'static/That_Was_Easy_IMG/')

        #check if directory exists
        if not os.path.exists(path + current_day_path + str(latitude) + '_' + str(longitude)):
            os.makedirs(path + current_day_path + str(latitude) + '_' + str(longitude))

        #save image
        save_directory = path + current_day_path + str(latitude) + '_' + str(longitude) + '/'

        filename = str(latitude) + '_' + str(longitude) + '_' + str(degree) + '.jpeg'

        image.save(save_directory + filename)

        list_filenames.append(filename)

        image_paths.append(save_directory + filename)

        degree += 90

    return list_filenames, image_paths, path, save_directory


def stitch(list_filenames, image_paths):

    image1 = Image.open(image_paths[0])
    image2 = Image.open(image_paths[1])
    image3 = Image.open(image_paths[2])
    image4 = Image.open(image_paths[3])

    (width1, height1) = image1.size
    (width2, height2) = image2.size
    (width3, height3) = image3.size
    (width4, height4) = image4.size

    result_width = width1 + width2 + width3 + width4
    result_height = max(height1, height2, height3, height4)

    result = Image.new('RGB', (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(width1, 0))
    result.paste(im=image3, box=(width1 + width2, 0))
    result.paste(im=image4, box=(width1 + width2 + width3, 0))

    #result.show()

    return result

def get_qrcode(result, directory, latitude, longitude):
    #qr_img = qrcode.make(str(latitude) + ',' + str(longitude))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(str(latitude) + ',' + str(longitude))
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")

    (width, height) = result.size

    result.paste(im=qr_img, box=(0, 425))

    result.show()

def save_result(result, directory, latitude, longitude):

    current_day_path = get_datetime()

    result.save(directory + current_day_path + str(latitude) + '_' + str(longitude) + '.jpeg')

def cleanup(save_directory):
    #clean up directories
    shutil.rmtree(save_directory)


'''End of script functions '''

@app.route('/',methods=['GET', 'POST'])
def index():
    for root, dirs, files in os.walk("static/That_Was_Easy_IMG"):
        #print(root)
        print("*****")
        #print(files)
    string='That_Was_Easy_IMG/'
    i = 0
    filess=[]
    for s in files:
        filess.append(string + files[i])
        i = i + 1
    #print(filess)

    return render_template('index.html',filess=filess)

@app.route('/show',methods=['GET', 'POST'])
def imagesShow():

    lat=request.form.get('latitude')
    long=request.form.get('longitude')

    #print(lat)
    #print(long)
    api_key = inst_google()
    #34.06920798890698, -117.97529606801908
    latitude = lat
    longitude = long

    (list_filenames, image_paths, directory, save_directory) = get_google_maps_api(api_key, latitude, longitude)

    result = stitch(list_filenames, image_paths)
    #print(type(result))
    get_qrcode(result, directory, latitude, longitude)

    save_result(result, directory, latitude, longitude)

    cleanup(save_directory)
    current_day_path = get_datetime()
    path= 'That_Was_Easy_IMG/'  + current_day_path + str(latitude) + '_' + str(longitude) + '.jpeg'
    print(path)
    print('done')

    for root, dirs, files in os.walk("static/That_Was_Easy_IMG"):
        #print(root)
        print("*****")
        #print(files)
    latt=latitude
    longg=longitude
    return render_template('images.html',path=path,latt=latt,longg=longg)


if __name__ == '__main__':
    # do not change the ip nor the port that is used for the app
    app.run(host='127.0.0.1', port=8080)
