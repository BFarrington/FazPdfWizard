import io
import cv2
import os
import pytesseract
from PyPDF2 import PdfReader, PdfWriter

print('~~~~~~~~~~~~~~~~~~~~~~~~~')
print('     Faz PDF Wizard      ')
print('~~~~~~~~~~~~~~~~~~~~~~~~~')
print('Enter input video:')
video_name = input()
print('Enter output pdf:')
pdf_name = input()
print('~~~~~~~~~~~~~~~~~~~~~~~~~')
print('starting...')


video = cv2.VideoCapture(video_name)
fps= video.get(cv2.CAP_PROP_FPS)

frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
count = 0
pdf_pages = []
prev_frame = None
while count < frames:
    video.set(cv2.CAP_PROP_POS_FRAMES,count)
    ret, frame = video.read()
    if frame is None:
        break
    else:
        width = frame.shape[1]
        height = frame.shape[0]
        frame = frame[0:height, 0+int(width/4):width-int(width/4)]
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    if prev_frame is not None:
        diff = cv2.absdiff(frame_gray, prev_frame)
        thresh_diff = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)[1]
        total_pixels = frame_gray.shape[0] * frame_gray.shape[1] * 1.0
        diff_on_pixels = cv2.countNonZero(thresh_diff) * 1.0
        difference_measure = diff_on_pixels / total_pixels
        if difference_measure > 0.05:
            print("Adding page - Difference measure: " + str(difference_measure) + " - Progress: " + str((count/frames*100).__floor__()) + "%")
            pdf = pytesseract.image_to_pdf_or_hocr(frame, lang='eng',extension='pdf')
            pdf_pages.append(pdf)
    else:
        pdf = pytesseract.image_to_pdf_or_hocr(frame, lang='eng',extension='pdf')
        pdf_pages.append(pdf)
    prev_frame = frame_gray
    count += 5

print('~~~~~~~~~~~~~~~~~~~~~~~~~')
pdf_writer = PdfWriter()
for page in pdf_pages:
  pdf = PdfReader(io.BytesIO(page))
  insert = pdf.pages[0]
  insert.compress_content_streams()
  if(insert.extract_text().__len__()>50):
    print("Writing page")
    pdf_writer.add_page(insert)
  
file = open(pdf_name, 'wb')
pdf_writer.write(file)
file.close()
print('~~~~~~~~~~~~~~~~~~~~~~~~~')
print('Collected Pages'+str(pdf_pages.__len__()))
print('Printed page count:'+str(pdf_writer.getNumPages()))