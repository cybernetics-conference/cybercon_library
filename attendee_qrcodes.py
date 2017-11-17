import os
import qrcode

QR_PATH = 'data/qrcodes/attendees'

id = 'A:test'
img = qrcode.make(id, border=0)
fname = '{}.png'.format(id)
img.save(os.path.join(QR_PATH, fname))