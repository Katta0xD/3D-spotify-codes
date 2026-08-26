import requests
import meshlib.mrmeshpy as mr
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from io import BytesIO

WHITE = 255  # i don't think this is necessary, since the range 0-255 is yield by PIL.Image.convert
HEIGHT = 100  # 10


def search(searchTerm, reference):
    print()


def send(reference, URI, style):
    c = Content(reference, URI)
    c.getCodeImage()
    c.saveImage()
    c.create3DModel(style)
    c.save3DModel()


class Content:
    def __init__(self, reference, URI):

        if reference.find("<") + reference.find(">") + reference.find(
            ":"
        ) + reference.find('"') + reference.find("\\") + reference.find(
            "/"
        ) + reference.find("|") + reference.find("?") + reference.find("*") > -(9):
            raise ValueError("Bad reference")
        else:
            self.reference = reference

        try:
            URI = URI.split("?")[0]
            terms = URI.split("/")
            self.contentType = terms[3]
            self.id = terms[4]
        except Exception:
            raise ValueError("Bad link")
        file = open("config.txt", "r")
        lines = file.readlines()
        savePath = lines[1].split("=")[1].replace("\n", "")
        if savePath.endswith("/"):
            savePath = savePath[:-1]
        self.imageSavePath = f"{savePath}/images/"
        self.modelSavePath = f"{savePath}/models/"

        self.image: Image.Image
        self.modelImage: Image.Image
        self.model: mr.Mesh

    def getCodeImage(self):
        size = "2047"  # width pixels. higher: 2047, lower: 256
        format = "png"  # {png, jpeg, svg}
        bgColor = "000000"  # hexadecimal color
        barColor = "white"  # {white, black}
        #                                     format     barColor          content-type
        # https://scannables.scdn.co/uri/plain/svg/000000/white/640/spotify:track:3ODBAK028eyO1KFK9tt9G4
        #                                         bgColor      size              id
        print(
            f"https://scannables.scdn.co/uri/plain/{format}/{bgColor}/{barColor}/{size}/spotify:{self.contentType}:{self.id}"
        )
        try:
            response = requests.get(
                f"https://scannables.scdn.co/uri/plain/{format}/{bgColor}/{barColor}/{size}/spotify:{self.contentType}:{self.id}"
            )
            self.image = Image.open(BytesIO(response.content)).convert("L")
        except Exception:
            raise ValueError("Bad Link")

    def saveImage(self):
        self.image.save(f"{self.imageSavePath}{self.reference}-code.png", "PNG")

    def create3DModel(self, style=1):
        def modelFromImage(pilImg: Image.Image):

            npImg = np.array(pilImg)
            mrImage = mr.Image()
            height, width = npImg.shape
            mrImage.resolution = mr.Vector2i(width, height)
            for x in npImg.flatten():
                mrImage.pixels.append(mr.Color(x, x, x))

            # Extrude Image to create a mesh
            distanceMap = mr.convertImageToDistanceMap(mrImage, 0)
            polyline = mr.distanceMapTo2DIsoPolyline(distanceMap, isoValue=127)
            mesh = mr.triangulateContours(polyline.contours())
            mr.addBaseToPlanarMesh(mesh, zOffset=30)

            return mesh

        def style1():
            leftExtention = 170
            ringRadius = leftExtention / 2

            canvasW, canvasE = self.image.size
            canvasW = canvasW + leftExtention
            image = Image.new("L", (canvasW, canvasE), 255)
            draw = ImageDraw.Draw(image)
            radius = canvasE // 2
            draw.rounded_rectangle(
                (leftExtention, 0, canvasW, canvasE),
                radius=radius,
                fill=0,
            )

            imgLogo = self.image.crop((150, 187, 372, 331))
            imgLogo = ImageOps.invert(imgLogo)
            imgLogo.tobytes()
            imgLogo = ImageOps.scale(imgLogo, 1.6)
            image.paste(imgLogo, (86 + leftExtention, 140))

            imgCode = self.image.crop((511, 102, 1944, 408))
            image.paste(imgCode, (511 + leftExtention, 102))

            image.show()

            imgRing = Image.new("L", (canvasW, canvasE), color=255)
            draw = ImageDraw.Draw(imgRing)
            draw.circle((leftExtention, canvasE / 2), ringRadius, 0)
            maskRing = ImageOps.invert(imgRing)
            draw.circle((leftExtention, canvasE / 2), ringRadius * (2 / 3), 255)

            image.paste(imgRing, mask=maskRing)

            image = ImageOps.expand(
                image, 10, 255
            )  # This is so the the countours() method can find the whole objetct

            image.show()
            return image

        def style2():
            print()

        match style:
            case 1:
                self.modelImage = style1()
                self.model = modelFromImage(self.modelImage)
            case 2:
                style2()
            case _:
                print("this shouldn't have happened")

    def save3DModel(self):
        mr.saveMesh(self.model, f"{self.modelSavePath}{self.reference}.stl")
        self.modelImage.save(f"{self.imageSavePath}{self.reference}-model.png", "PNG")
