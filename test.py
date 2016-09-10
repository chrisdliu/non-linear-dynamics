from PIL import Image

img = Image.open('map.png')
pixels = img.load()
print(img.size)
print(pixels[7,5])