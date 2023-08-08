from ContentsBased import ContentBasedRecommendation

csv_filepath = './data/review_product_data_example.csv'
recommender = ContentBasedRecommendation(csv_filepath)

recommender.make_recommendation()

# import os

# current_dir = os.path.dirname(os.path.abspath(__file__))
# print(current_dir)
# csv_filepath = os.path.join(current_dir, '..', 'review_data1.csv')
# print(csv_filepath)