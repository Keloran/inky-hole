import os
import json
import urllib2
from inky import InkyPHAT
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
from dotenv import load_dotenv

# DotEnv
load_dotenv()

# Get inky_display
inky_display = InkyPHAT("black")
inky_display.set_border(inky_display.WHITE)

# Set current directory

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Weather
class Weather:
    MainDesc = ""
    SubDesc1 = ""
    SubDesc2 = ""
    Icon = ""
    TempCelcius = ""
    TempCelciusFeels = ""
    WindSpeed = ""
    WindDirection = ""

    FontSize = 16
    FontSizeLarge = 16
    Draw = None
    InkyDisplay = None

    def __init__(self, fontsize, fontsize_large, draw, inky_display):
        self.Draw = draw
        self.FontSize = fontsize
        self.FontSizeLarge = fontsize_large
        self.InkyDisplay = inky_display

        try:
            f = urllib2.urlopen("https://api.openweathermap.org/data/2.5/weather?lat=" + os.environ['WEATHER_LAT'] + "&lon=" + os.environ['WEATHER_LON'] + "&appid=" + os.environ['WEATHER_API'])
            json_string = f.read()
            parsed_json = json.loads(json_string)
            for weather in parsed_json["weather"]:
                main = weather["main"]
                desc = weather["description"]
                icon = weather["icon"]

            temp = parsed_json["main"]
            wind = parsed_json["wind"]

            f.close()
        except:
            main = "?"
            desc = "?"
            icon = ""
            temp = "?"
            wind = ""

        self.MainDesc = main
        self.Icon = icon
        self.SubDesc(desc)

        if temp != "?":
            self.Temp(temp)
            self.Wind(wind)

    def create_mask(self, source):
        mask=(self.InkyDisplay.RED, self.InkyDisplay.WHITE, self.InkyDisplay.BLACK)
        mask_image = Image.new("1", source.size)
        w, h = source.size
        for x in range(w):
            for y in range(h):
                p = source.getpixel((x, y))
                if p in mask:
                    mask_image.putpixel((x, y), 255)

        return mask_image

    def icon_draw(self, img):
        self.Draw.rectangle((140, 10, 180, 60), fill=self.InkyDisplay.BLACK, outline=self.InkyDisplay.WHITE)

        imgPos = (140, 10)
        im = Image.new("P", (40, 40))
        foundImg = False

        if self.Icon == "01d" or self.Icon == "01n":
            im = Image.open("./resources/icon-sun.png")
            foundImg = True
        elif self.Icon == "04d" or self.Icon == "04n":
            im = Image.open("./resources/icon-cloud.png")
            foundImg = True
        elif self.Icon == "10d" or self.Icon == "10n":
            im = Image.open("./resources/icon-rain.png")
            foundImg = True
        elif self.Icon == "11d" or self.Icon == "11n":
            im = Image.open("./resources/icon-storm.png")
            foundImg = True
        elif self.Icon == "13d" or self.Icon == "13n":
            im = Image.open("./resources/icon-snow.png")
            foundImg = True

        if foundImg:
            mask = self.create_mask(im)
            img.paste(im, imgPos, mask)
        else:
            font2 = ImageFont.truetype(FredokaOne, self.FontSize)
            self.Draw.text((140, 20), self.MainDesc, self.InkyDisplay.BLACK, font2)

        return img


    def SubDesc(self, wdesc):
        t = wdesc.split(" ")
        if len(t) > 1:
            wdesc1 = t[0]
            wdesc2 = t[1]
        else:
            wdesc1 = wdesc
            wdesc2 = ""

        self.SubDesc1 = wdesc1
        self.SubDesc2 = wdesc2

    def Temp(self, temp):
        self.TempCelcius = temp["temp"] - 273.15
        self.TempCelciusFeels = temp["feels_like"] - 273.15

    def Wind(self, wind):
        self.WindSpeed = str(wind["speed"] * 2.237) + "mph"
        windDir = wind["deg"]

        if windDir > 0 and windDir < 46:
            self.WindDirection = "NE"
        elif windDir > 45 and windDir < 91:
            self.WindDirection = "E"
        elif windDir > 90 and windDir < 136:
            self.WindDirection = "SE"
        elif windDir > 135 and windDir < 181:
            self.WindDirection = "S"
        elif windDir > 180 and windDir < 226:
            self.WindDirection = "SW"
        elif windDir > 225 and windDir < 271:
            self.WindDirection = "W"
        elif windDir > 270 and windDir < 316:
            self.WindDirection = "NW"
        else:
            self.WindDirection = "N"

    def Render(self, img):
        img = self.icon_draw(img)
        font2 = ImageFont.truetype(FredokaOne, self.FontSize)
        draw.text((140, 60), self.SubDesc1, self.InkyDisplay.BLACK, font2)
        draw.text((140, 70), self.SubDesc2, self.InkyDisplay.BLACK, font2)

        #str("%.1f" % round(self.RatioBlocked, 2))

        cPos = (186 + ((self.FontSizeLarge / 2) * len(str("%.0f" % self.TempCelcius)))) 
        font3 = ImageFont.truetype(FredokaOne, self.FontSizeLarge)
        font4 = ImageFont.truetype(FredokaOne, self.FontSizeLarge + 3)
        fontC = ImageFont.truetype(FredokaOne, self.FontSize - 5)
        draw.text((183, 10), str("%.0f" % self.TempCelcius), self.InkyDisplay.BLACK, font3)
        draw.text((cPos, 10), "C", self.InkyDisplay.BLACK, fontC)
        draw.text((183, 30), str("%.0f" % self.TempCelciusFeels), self.InkyDisplay.BLACK, font3)
        draw.text((cPos, 30), "C", self.InkyDisplay.BLACK, fontC)

        draw.text((180, 70), self.WindDirection, self.InkyDisplay.BLACK, font4)

        return img

# PiHole
class PiHole:
    AdsBlocked = ""
    RatioBlocked = ""

    FontSize = None
    Draw = None
    InkyDisplay = None

    def __init__(self, fontsize, draw, inky_display):
        adsblocked1, ratioblocked1 = self.pihole(os.environ['PIHOLE_PRIMARY'])
        adsblocked2, ratioblocked2 = self.pihole(os.environ['PIHOLE_SECONDARY'])

        self.AdsBlocked = (adsblocked1 + adsblocked2)
        self.RatioBlocked = (ratioblocked1 + ratioblocked2)
        
        self.FontSize = fontsize
        self.Draw = draw
        self.InkyDisplay = inky_display

    def pihole(self, addr):
        try:
            f = urllib2.urlopen(addr)
            json_string = f.read()
            parsed_json = json.loads(json_string)
            adsblocked = parsed_json['ads_blocked_today']
            ratioblocked = parsed_json['ads_percentage_today']
            f.close()
        except:
            adsblocked = ''
            ratioblocked = ''

        return adsblocked, ratioblocked

    def Render(self):
        font = ImageFont.truetype(FredokaOne, self.FontSize)

        self.Draw.text((20,20), str(self.AdsBlocked), self.InkyDisplay.BLACK, font)
        self.Draw.text((20,50), str("%.1f" % round(self.RatioBlocked, 2)) + "%", self.InkyDisplay.BLACK, font)

# Seperator
class Seperator:
    InkyDisplay = None
    Draw = None

    def __init__(self, draw, inky_display):
        self.InkyDisplay = inky_display
        self.Draw = draw

    def Render(self):
        self.Draw.text((120, 0), "|", self.InkyDisplay.BLACK, ImageFont.truetype(FredokaOne, 32))
        self.Draw.text((120, 30), "|", self.InkyDisplay.BLACK, ImageFont.truetype(FredokaOne, 32))
        self.Draw.text((120, 60), "|", self.InkyDisplay.BLACK, ImageFont.truetype(FredokaOne, 32))
    

# Output
print "Inky Start"
img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
draw = ImageDraw.Draw(img)

print "Start PiHole"
pihole = PiHole(32, draw, inky_display)
pihole.Render()
print "End PiHole"

print "Start Weather"
w = Weather(12, 18, draw, inky_display)
img = w.Render(img)
print "End Weather"

print "Start Seperator"
s = Seperator(draw, inky_display)
s.Render()
print "End Seperator"

inky_display.set_image(img)
inky_display.h_flip = True
inky_display.v_flip = True
inky_display.show()
print "Inky Finish"
