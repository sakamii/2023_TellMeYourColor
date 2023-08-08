import os
from flask import Flask, request, render_template, session, redirect, url_for, send_from_directory
# from flask_restful import Api, Resource
from flask_cors import CORS
from flask import jsonify
from PIL import Image
from models.find_personal_color import SkinToneClassifier # 얼굴 모델
from models.ContentsBased import ContentBasedRecommendation # 추천 깡통(연습)
from database import img_path
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
import random
import string
import pymysql
import json
# from data import get_data_from_table

# db_path = 'mysql+pymysql://tmyc:80344I@192.168.0.66:3306/tmyc'
# engine = create_engine(db_path)

def generate_secret_key(length=32):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

app = Flask(__name__)
app.secret_key = generate_secret_key()
CORS(app)
UPLOAD_FOLDER = './static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URL'] = 'mysql+pymysql://tmyc:80344I@192.168.0.66:3306/tmyc'
db.init_app(app)






# mysql_host = '192.168.0.66'
# mysql_user = 'tmyc'
# mysql_password = '8O344I'
# mysql_db = 'tmyc'

# def connect_db():
#     connection = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_db)
#     return connection

# 데이터를 가져오는 함수
# 추천 완료 후 마지막 페이지에서 상품 보여줄 때
# 상품을 찾기위한 데이터
# (product, price, color_name, type, total_rating, rating_count, brand, product_id)
# def get_data_from_database():
#     try:
#         connection = connect_db()
#         with connection.cursor() as cursor:
#             sql = 'SELECT * FROM data_default;' # sql query 작성
#             cursor.execute(sql) # query 실행
#             result = cursor.fetchall() # 모든 행 가져오기
#             return result
#     except Exception as e:
#         print('error', e)
#     finally:
#         connection.close()

# user_id 컬럼의 nickname, id가 존재하는지의 대한 판단
@app.route('/user_id_exist', methods=['POST'])
def check_nickname_exist():
    user_id_data = get_data_from_table(table_1_name, table_1_columns)
    # data = get_data_from_database()
    user_ids = [record[0] for record in user_id_data]
    AppData.nickname = app_data.nickname
    if AppData.nickname in user_ids:
        response = ({'result': True})
    else:
        response = ({'result': False})
    return jsonify(response)

@app.route('/review_counts', methods=['GET'])
def check_review_count():
    user_id_data = get_data_from_table(table_1_name, table_1_columns)
    review_counts = {record[0]: record[1] for record in user_id_data}
    AppData.nickname = app_data.nickname
    review_count = review_counts[AppData.nickname]
    if review_count >= 10:
        return jsonify({'result': True, 'review_count': review_count})
    else:
        return jsonify({'result': False, 'review_count': review_count})
    

# check_nickname_exist(user_id_data)

# @app.route('/user_review_csv')
# def check_nickname_exist():
#     data = get_data_from_database()
#     user_ids = [record[0] for record in data]
#     review_counts = {record[0]: record[1] for record in data}
#     AppData.nickname = app_data.nickname

#     if AppData.nickname in user_ids:
#         review_count = review_counts[AppData.nickname]
#         if review_count >= 10:
#             return jsonify({'result':True})
#         else:
#             return jsonify({'result':False})
#     else:
#         return jsonify({'result':False})

@app.route('/')
def main():
    return render_template('main.html')

class AppData:
    nickname = None

app_data = AppData()

# 사용자의 이미지, 닉네임을 입력받은 값을 서버에서 받아 이미지는 저장해주고
# nickname 값은 class 변수에 저장
@app.route('/second', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        image_file = request.files['image']
        nickname = request.values['nickname']
        
        if image_file is not None:
            image_name = 'img.jpg'
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
            
            image_file.save(image_path)
            print(image_path)

            app_data.nickname = nickname
            print(app_data.nickname)
        
            # season, person, explain = get_prediction_data(image_path)

            # response = {
            #     'season': season,
            #     'person': person,
            #     'explain': explain
            # }
            
            return jsonify(response)
        else:
            response = {'message': 'No image file received'}
            return jsonify(response), 400
    else:
        return render_template('second.html')
    
# 이미지 파일을 사용하는 퍼스널 컬러 진단 모델
def get_prediction_data(image_path):
    classifier = SkinToneClassifier()
    cropped_face = classifier._get_face_region(image_path)

    if cropped_face is not None:
        skin_tone = classifier.classify_skin_tone(image_path)

        if skin_tone == 'spring_warm':
            season = '봄 웜'
            person = '#수지, #아이유, #이제훈'
            explain = '따뜻한 갈색 계열의 옷을 입었을 때 얼굴이 생기 있어 보이고, 오렌지(orange, 주황색)나 코럴(coral, 연한 분홍색) 계열의 색조 화장품이 잘 어울리며, 실버(silver, 은색)보다는 골드(gold, 금색) 액세서리가 자연스럽게 어울립니다. 봄웜톤의 경우 명도와 채도가 높은 노란빛이 도는 화사하고 밝은 느낌의 컬러가 잘 어울리며 어두운 색과는 맞지 않습니다.'
        elif skin_tone == 'summer_cool':
            season = '여름 쿨'
            person = '#손예진, #아이린, #김연아'
            explain = '분홍색과 하얀색 계열의 옷을 입었을 때 얼굴이 생기 있어 보이고, 분홍빛 색조 화장품이 잘 어울리며 골드(gold, 금색)보다는 실버(silver, 은색) 액세서리가 자연스럽게 어울립니다. 여름쿨톤의 경우 명도와 채도가 높은 푸른빛이 도는 화사하고 밝은 느낌의 컬러가 잘 어울리며 검정색과 주황빛이 도는 색깔은 어울리지 않습니다.'
        elif skin_tone == 'fall_warm':
            season = '가을 웜'
            person = '#제니, #유승호, #이효리'
            explain = '따뜻한 갈색 계열의 옷을 입었을 때 얼굴이 생기 있어 보이고, 오렌지(orange, 주황색)나 코럴(coral, 연한 분홍색) 계열의 색조 화장품이 잘 어울리며, 실버(silver, 은색)보다는 골드(gold, 금색) 액세서리가 자연스럽게 어울립니다. 가을웜톤의 경우 명도와 채도가 낮은 노란빛이 도는 흐리고 어두운 느낌의 컬러가 잘 어울리며 파란빛이 도는 색깔은 어울리지 않습니다.'
        else:
            season = '겨울 쿨'
            person = '#임지연, #이동욱, #카리나'
            explain = '분홍색과 하얀색 계열의 옷을 입었을 때 얼굴이 생기 있어 보이고, 분홍빛 색조 화장품이 잘 어울리며 골드(gold, 금색)보다는 실버(silver, 은색) 액세서리가 자연스럽게 어울립니다. 겨울쿨톤의 경우 명도와 채도의 높고 낮음에 관계없이 푸른빛이 도는 선명하고 강한 컬러가 잘 어울리며 여름쿨톤과는 반대로 검정색 또한 잘 어울립니다. 베이지와 주황빛이 도는 색깔은 어울리지 않습니니다.'

        return season, person, explain  
    else:
        season = '얼굴이 없으십니다.'
        person = ''
        explain = ''

        return season, person, explain

# result.html에게 nickname을 응답해 준다.
@app.route('/give_nickname', methods=['GET'])
def give_nickname():
    # nickname = request.form.get('nickname')
    AppData.nickname = app_data.nickname
    return app_data.nickname

# result.html에게 nickname의 값이 있거나 없거나 응답해 준다. 
# @app.route('/check_nickname', methods=['POST'])
# def check_nickname():
#     # nickname = request.form.get('nickname')

#     AppData.nickname = app_data.nickname

#     if AppData.nickname:
#         response = {'result': True}
#     else:
#         response = {'result': False}
#     return jsonify(response)

# get_prediction_data 함수를 사용해서 퍼스널 컬리 진단 결과를 result로 보내준다.
@app.route('/result', methods=['GET', 'POST'])
def result_page():
    # print('app_data', app_data.nickname)
    image_path = './static/img/img.jpg'
    # nickname = request.form.get('nickname')
    # print('nickname', nickname)

    AppData.nickname = app_data.nickname

    # if not nickname:
    #     nickname = '사용자'
    season, person, explain = get_prediction_data(image_path)
    return render_template('result.html', people=AppData.nickname, season=season, person=person, explain=explain, image_url=image_path)    

# content_based로 연결 되도록 라우터 정의
@app.route('/content_based')
def content_based():
    return render_template('content_based.html')


# @app.route('/user_csv', methods=['POST'])
# def user_csv_file():
#     user_file = './user_review_cnt.csv'
#     data = pd.read_csv(user_file)

# lip_item = [{
#     "imgSrc": "http://127.0.0.1:5000/static/img/img.jpg",
#     # 'colorSrc': "http://127.0.0.1:5000/static/img/IMG_9900.jpg",
#     "brand": "샤넬",
#     "item_name": "립혜쉰",
#     "color": "빨강",
#     "price": "1원"
# },
# {
#     "imgSrc": "http://127.0.0.1:5000/static/img/img.jpg",
#     "brand": "샤넬",
#     "item_name": "아이새도우",
#     "color": "브라운",
#     "price": "2원"
# },
# {
#     "imgSrc": "http://127.0.0.1:5000/static/img/img.jpg",
#     "brand": "샤넬",
#     "item_name": "아이새도우",
#     "color": "브라운",
#     "price": "3원"
# }]

# eyeshadow_item = [{
#     "imgSrc": "http://127.0.0.1:5000/static/img/img.jpg",
#     "brand": "디올",
#     "item_name": "아이새도우",
#     "color": "브라운",
#     "price": "1원"
# },
# {
#     "imgSrc": "http://127.0.0.1:5000/static/img/img.jpg",
#     "brand": "디올",
#     "item_name": "아이새도우",
#     "color": "브라운",
#     "price": "2원"
# },
# {
#     "imgSrc": "http://127.0.0.1:5000/static/img/img.jpg",
#     "brand": "디올",
#     "item_name": "아이새도우",
#     "color": "브라운",
#     "price": "3원"
# }]

# blusher_item = [{
#     "imgSrc": "http://127.0.0.1:5000/static/img/img.jpg",
#     "brand": "랑콤",
#     "item_name": "블러셔",
#     "color": "핑크",
#     "price": '1원'
# },
# {
#     "imgSrc": "http://127.0.0.1:5000/static/img/img.jpg",
#     "brand": "랑콤",
#     "item_name": "아이새도우",
#     "color": "브라운",
#     "price": "2원"
# },
# {
#     "imgSrc": "http://127.0.0.1:5000/static/img/img.jpg",
#     "brand": "랑콤",
#     "item_name": "아이새도우",
#     "color": "브라운",
#     "price": "3원"
# }]

# final_page에 상품 추천 결과물을 보내주는 코드
@app.route('/iteminfo', methods=['POST'])
def get_item_info():
    data = request.get_json()
    item_type = data.get('item_type')
    
    if item_type == 'lip':
        result_item = lip_item
    elif item_type == 'eyeshadow':
        result_item = eyeshadow_item
    elif item_type == 'blusher':
        result_item = blusher_item
    else:
        result_item = []

    return jsonify(result_item)


@app.route('/get_nickname', methods=['GET'])
def get_nickname():
    nickname = session.get('nickname', None)
    print(nickname)
    return jsonify({'nickname': nickname})


csv_filepath = './models/data/review_product_data_example.csv'
recommender = ContentBasedRecommendation(csv_filepath)

@app.route('/recommend', methods=['GET'])
def product():
    nickname_response = get_nickname()
    print(nickname_response)
    result = recommender.make_recommendation(nickname_response, user_nickname)
    return jsonify({'result': result})
    
@app.route('/final_page')
def final_page():
    return render_template('final_page.html')

if __name__ == '__main__':
    app.run(debug=True)

