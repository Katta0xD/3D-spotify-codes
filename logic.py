import requests
import numpy as np
from PIL import Image
from io import BytesIO
from stl import Mesh, mesh

WHITE = 255  # i don't think this is necessary, since the range 0-255 is yield by PIL.Image.convert
HEIGHT = 10


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
        self.reference = reference

        URI = URI.split("?")[0]
        terms = URI.split("/")
        self.contentType = terms[3]
        self.id = terms[4]

        file = open("config.txt", "r")
        lines = file.readlines()
        savePath = lines[1].split("=")[1].replace("\n", "")
        self.saveImagePath = f"{savePath}/images/"
        self.saveModelPath = f"{savePath}/models/"

        self.image: Image.Image
        self.model: mesh.Mesh

    def getCodeImage(self):
        size = "1280"  # width pixels. higher: 2047, lower: 256
        format = "png"  # {png, jpeg, svg}
        bgColor = "000000"  # hexadecimal color
        barColor = "white"  # {white, black}
        #                                     format     barColor          content-type
        # https://scannables.scdn.co/uri/plain/svg/000000/white/640/spotify:track:3ODBAK028eyO1KFK9tt9G4
        #                                         bgColor      size              id
        print(
            f"https://scannables.scdn.co/uri/plain/{format}/{bgColor}/{barColor}/{size}/spotify:{self.contentType}:{self.id}"
        )

        response = requests.get(
            f"https://scannables.scdn.co/uri/plain/{format}/{bgColor}/{barColor}/{size}/spotify:{self.contentType}:{self.id}"
        )
        self.image = Image.open(BytesIO(response.content))

    def saveImage(self):
        self.image.save(f"{self.saveImagePath}{self.reference}{self.id}.png", "PNG")

    def create3DModel(self, style):
        def isInnerPixel(image, x, y):
            isInner = False
            if (
                image[x][y + 1] == WHITE
                and image[x][y - 1] == WHITE
                and image[x + 1][y] == WHITE
                and image[x - 1][y] == WHITE
            ):
                isInner = True
            return isInner

        # convert the image into a mtrix of -1/WHITE values
        img = self.image.crop((256, 0, 1280, 320))
        img = img.convert("L")
        img = np.array(img)
        height, width = img.shape
        for i in range(height):
            for j in range(width):
                if img[i][j] > 1:
                    img[i][j] = WHITE

        Image.fromarray(img, "L").show()

        # search for the "bars". store arrays of those pixels to create faces of the 2D model later.
        accounted = np.zeros((height, width), dtype=bool)
        bars = np.empty(23, dtype=object)
        triangleCount = 0
        barCount = 0
        # These "-1" are a horrible hack to avoid accesing memory off the image segment, when i2 = height or j2 = width. but since we know there is no white segment all over the border of the image, it'll work
        for i in range(height - 1):
            for j in range(width - 1):
                print(f"{i}/{height - 0}, {j}/{width - 1}")
                if (
                    img[i][j] == WHITE
                    and not accounted[i][j]
                    and not isInnerPixel(img, i, j)
                ):
                    print(f"{barCount + 1}/23")
                    i2 = i
                    j2 = j
                    bar = []
                    # 8-way cheking to follow the bar
                    while True:  # Here, in a more general context, there would be needed restrictions to not try to access memory off the memory segment of image, but knowing the nature of the code
                        # images we know a white segment will never be found on the last or first pixel, neither vertical nor horizontal
                        print(f"(bar number: {barCount + 1} ({i2} - {j2})")
                        if (
                            img[i2][j2 + 1] == WHITE
                            and not accounted[i2][j2 + 1]
                            and not isInnerPixel(img, i2, j2 + 1)
                        ):  # →
                            j2 += 1
                        elif (
                            img[i2 + 1][j2 + 1] == WHITE
                            and not accounted[i2 + 1][j2 + 1]
                            and not isInnerPixel(img, i2 + 1, j2 + 1)
                        ):  # ↘
                            i2 += 1
                            j2 += 1
                        elif (
                            img[i2 + 1][j2] == WHITE
                            and not accounted[i2 + 1][j2]
                            and not isInnerPixel(img, i2 + 1, j2)
                        ):  # ↓
                            i2 += 1
                        elif (
                            img[i2 + 1][j2 - 1] == WHITE
                            and not accounted[i2 + 1][j2 - 1]
                            and not isInnerPixel(img, i2 + 1, j2 - 1)
                        ):  # ↙
                            i2 += 1
                            j2 -= 1
                        elif (
                            img[i2][j2 - 1] == WHITE
                            and not accounted[i2][j2 - 1]
                            and not isInnerPixel(img, i2, j2 - 1)
                        ):  # ←
                            j2 -= 1
                        elif (
                            img[i2 - 1][j2 - 1] == WHITE
                            and not accounted[i2 - 1][j2 - 1]
                            and not isInnerPixel(img, i2 - 1, j2 - 1)
                        ):  # ↖
                            i2 -= 1
                            j2 -= 1
                        elif (
                            img[i2 - 1][j2] == WHITE
                            and not accounted[i2 - 1][j2]
                            and not isInnerPixel(img, i2 - 1, j2)
                        ):  # ↑
                            i2 -= 1
                        elif (
                            img[i2 - 1][j2 + 1] == WHITE
                            and not accounted[i2 - 1][j2 + 1]
                            and not isInnerPixel(img, i2 - 1, j2 + 1)
                        ):  # ↗
                            i2 -= 1
                            j2 += 1

                        accounted[i2][j2] = True
                        bar.append((i2, j2))

                        if i2 == i and j2 == j:
                            break  # if the current pixel is equal to initial pixel

                    bar = np.array(bar)
                    triangleCount += len(bar) * 2
                    bars[barCount] = bar
                    barCount += 1

        faces = np.zeros(triangleCount, dtype=mesh.Mesh.dtype)
        counter = 0
        for i in range(23):
            startPoint = bars[i][0]
            for j in range(len(bars[i])):
                if j < len(bars[i]) - 1:
                    # print(f"bars[{i}][{j}]")
                    # if j > 400:
                    #    breakpoint()
                    faces[counter]["vectors"] = [
                        [*bars[i][j], 0],
                        [*bars[i][j], HEIGHT],
                        [*bars[i][j + 1], 0],
                    ]

                    faces[counter + 1]["vectors"] = [
                        [*bars[i][j], 0],
                        [*bars[i][j + 1], 0],
                        [*bars[i][j + 1], HEIGHT],
                    ]
                    """
                    faces[counter, 0] = [*bars[i][j], 0]
                    faces[counter, 1] = [*bars[i][j], HEIGHT]
                    faces[counter, 2] = [*bars[i][j + 1], 0]

                    faces[counter + 1, 0] = [*bars[i][j], HEIGHT]
                    faces[counter + 1, 1] = [*bars[i][j + 1], 0]
                    faces[counter + 1, 2] = [*bars[i][j + 1], HEIGHT]
                    """
                else:
                    faces[counter]["vectors"] = [
                        [*bars[i][j], 0],
                        [*bars[i][j], HEIGHT],
                        [*startPoint, 0],
                    ]

                    faces[counter + 1]["vectors"] = [
                        [*bars[i][j], 0],
                        [*startPoint, 0],
                        [*startPoint, HEIGHT],
                    ]
                    """
                    faces[counter, 0] = [*bars[i][j], 0]
                    faces[counter, 1] = [*bars[i][j], HEIGHT]
                    faces[counter, 2] = [*startPoint, 0]

                    faces[counter + 1, 0] = [*bars[i][j], HEIGHT]
                    faces[counter + 1, 1] = [*startPoint, 0] 
                    faces[counter + 1, 2] = [*startPoint, HEIGHT] 
                    """
                # counter += 1
                counter += 2

        modelMesh = mesh.Mesh(faces)
        self.model = modelMesh

    def save3DModel(self):
        self.model.save("model.stl")
