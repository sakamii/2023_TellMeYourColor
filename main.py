
# 정현호_이미지 크롤링
import crawl.imagecrawler
from crawl.imagecrawler import ImageCrawler
with ImageCrawler() as crawler:
    for celebrity, folder_name in crawl.imagecrawler.celebrities.items():
        crawler.download_images(celebrity, folder_name)

# 조세연_크롭핑 
# from face_crop.cropping import FaceEyeCropping
# face_eye_cropping = FaceEyeCropping()
# df = face_eye_cropping.make_dataframe()
# print(df)