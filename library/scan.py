import pygame
import pygame.camera
from PIL import Image
from pyzbar.pyzbar import decode

dim = (1280,720)
pygame.camera.init()
cams = pygame.camera.list_cameras()
cam = pygame.camera.Camera(cams[0], dim)
cam.start()


def scan():
    img = cam.get_image()
    img = pygame.image.tostring(img, 'RGBA', False)
    img = Image.frombytes('RGBA', dim, img)
    result = decode(img)
    return [r.data for r in result]