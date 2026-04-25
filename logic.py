import requests
import numpy as np
from PIL import Image
from io import BytesIO
from stl import mesh

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
        self.model = None

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
        # convert the image into a mtrix of 0/WHITE values
        img = self.image.crop((256, 0, 1280, 320))
        img = img.convert("L")
        img = np.array(img)
        height, width = img.shape
        for i in range(height):
            for j in range(width):
                if img[i][j] > 0:
                    img[i][j] = WHITE

        # search for the "islands". store arrays of those pixels to create faces of the 3D model later.
        accounted = np.zeros((width, height), dtype=bool)
        islands = []
        for i in range(width):
            for j in range(height):
                if not accounted[i][j]:
                    accounted[i][j] = True
                    if img[i][j] == WHITE:
                        i2 = i
                        j2 = j
                        island = []
                        # 8-way cheking to follow the bar
                        while True:  # Here, in a more general context, there would be needed restrictions to not try to access memory off the memory segment of image, but knowing the nature of the code
                            # images we know a white segment will never be found on the last or first pixel, neither vertical nor horizontal
                            if img[i2][j2 + 1] == WHITE:
                                i2 += 1
                            elif img[i2 + 1][j2 + 1] == WHITE:
                                i2 += 1
                                j2 += 1
                            elif img[i2 + 1][j2] == WHITE:
                                j2 += 1
                            elif img[i2 + 1][j2 - 1] == WHITE:
                                i2 += 1
                                j2 -= 1
                            elif img[i2][j2 - 1] == WHITE:
                                j2 -= 1
                            elif img[i2 - 1][j2 - 1] == WHITE:
                                i2 += 1
                                j2 -= 1
                            elif img[i2 - 1][j2] == WHITE:
                                i2 -= 1
                                j2 -= 1
                            elif img[i2 - 1][j2 + 1] == WHITE:
                                i2 -= 1
                                j2 += 1

                            accounted[i2][j2] = True
                            island.append((i2, j2))

                            if i2 == i and j2 == j:
                                break  # if the current pixel is equal to initial pixel
                        islands.append(island)

        faces = []
        for i in range(len(islands)):
            startIsland = islands[i]
            for j in range(islands[i].len()):
                if j < islands[i].len() - 1:
                    faces.append(
                        (
                            (*islands[i][j], 0),
                            (*islands[i][j], HEIGHT),
                            (*islands[i][j + 1], 0),
                        )
                    )
                    faces.append(
                        (
                            (*islands[i][j], 0),
                            (*islands[i][j], HEIGHT),
                            (*islands[i][j + 1], HEIGHT),
                        )
                    )
                else:
                    faces.append(
                        (
                            (*islands[i][j], 0),
                            (*islands[i][j], HEIGHT),
                            (*startIsland, 0),
                        )
                    )
                    faces.append(
                        (
                            (*islands[i][j], 0),
                            (*islands[i][j], HEIGHT),
                            (*startIsland, HEIGHT),
                        )
                    )

        faces = np.array(faces)
        modelMesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        modelMesh.vectors = faces
        self.model = modelMesh

    def save3DModel(self):
        self.model.save("model.stl")
