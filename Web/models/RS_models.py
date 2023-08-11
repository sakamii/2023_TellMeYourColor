
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# popularity score keyword
def keywords_processing(keywords):
    # keywords예시
        # USER_KEYWORD = {
        #     'tags':['잡티', '각질', '트러블'],
        #     'skin_tone':'중성',
        #     'score_weight':'발색력'
        # }
    new_row = {
        'product_idx':-1,
        'tag1':0,
        'tag2':0,
        'tag3':0,
        'tag4':0,
        'tag5':0,
        'tag6':0,
        'tag7':0,
        'tag8':0,
        'tag9':0,
        'skin_type1':0,
        'skin_type2':0,
        'skin_type3':0,
        'skin_type4':0,
        'skin_type5':0,
    }

    for tag in keywords['tags']:
        if tag ==  '잡티':
            new_row['tag1']=1
        elif tag ==  '각질':
            new_row['tag2']=1
        elif tag == '트러블':
            new_row['tag3']=1
        elif tag == '민감성':
            new_row['tag4']=1
        elif tag == '모공':
            new_row['tag5']=1
        elif tag == '홍조':
            new_row['tag6']=1
        elif tag == '아토피':
            new_row['tag7']=1
        elif tag == '주름':
            new_row['tag8']=1
        elif tag == '피지과다':
            new_row['tag9']=1

    if keywords['skin_type'] == '지성':
        new_row['skin_type1']=1
    elif keywords['skin_type'] == '건성':
        new_row['skin_type2']=1
    elif keywords['skin_type'] == '복합성':
        new_row['skin_type3']=1
    elif keywords['skin_type'] == '약건성':
        new_row['skin_type4']=1
    elif keywords['skin_type'] == '중성':
        new_row['skin_type5']=1

    if keywords['score_weight'] == '발색력':
        selected_detail_score = 'detail_score1'
    elif keywords['score_weight'] == '지속력':
        selected_detail_score = 'detail_score2'
    elif keywords['score_weight'] == '발림성':
        selected_detail_score = 'detail_score3'

    return new_row, selected_detail_score
def season(SKIN_TONE):
    seasons = {
        '봄웜':'b',
        '여름쿨':'s',
        '가을웜':'f',
        '겨울쿨':'w'
        
    }
    return seasons[SKIN_TONE]

# popularity score
def weighted_score(df, selected_detail_score, w=0.5):
    return w * df['color_score'] + (1 - w) * (df[selected_detail_score] + df['detail_socre1'] + df['detail_score2'] + df['detail_score3'] - df['weight']) / (3 - df['weight'])



def recommend(reco_rank, reco_size = 3):

    final_lips = list(reco_rank[reco_rank.product_type == '립'][:reco_size]['product_idx'])
    final_shadows = list(reco_rank[reco_rank.product_type == '섀도우'][:reco_size]['product_idx'])
    final_cheeks = list(reco_rank[reco_rank.product_type == '블러셔'][:reco_size]['product_idx'])

    # 추천 결과
    items_product_idx ={
        '립':final_lips,
        '섀도우':final_shadows,
        '블러셔':final_cheeks
    }
    
    return items_product_idx

def get_reco_prd_info(product_data, items_product_idx):
    
    item_info = {
        '립': '',
        '섀도우':'',
        '블러셔':''
    }

    
    for prd_type in items_product_idx:
        type_item_info = {
            "mainImg": [],
            "colorImg": [],
            "itemUrl": [],
            "brand": [],
            "itemName": [],
            "color": [],
            "price": []
        }

        for prd in items_product_idx[prd_type]:
            prd_info = product_data[product_data['product_idx']==prd]
            type_item_info['mainImg'].appned(prd_info['product_img'].values[0])
            type_item_info['colorImg'].appned(prd_info['color_img'].values[0])
            type_item_info['itemUrl'].appned(prd_info['product_link'].values[0])
            type_item_info['brand'].appned(prd_info['brand'].values[0])
            type_item_info['itemName'].appned(prd_info['product_name'].values[0])
            type_item_info['color'].appned(prd_info['color_name'].values[0])
            type_item_info['price'].appned(prd_info['price'].values[0])
            
        item_info[prd_type] = type_item_info
    
    return type_item_info

def popularity_based(recommend_data, product_score_data, keywords, SKIN_TONE):

    ######################db로 대체########################
    recommend_data = pd.read_csv("data/contents_based_all.csv")
    recommend_data.rename(columns = {'index':'product_idx', 'type':'product_type'}, inplace=True)
    product_score_data = pd.read_csv("data/score_data.csv")
    product_score_data.rename(columns={'detail_socre1':'detail_score1','index':'product_idx','type':'product_type'}, inplace=True)
    ########################################################

    new_row, selected_detail_score =  keywords_processing(keywords)

    RS_pop = recommend_data[recommend_data['skin_tone'].str.contains(SKIN_TONE)]
    RS_pop = RS_pop[['product_idx','tag1','tag2','tag3','tag4','tag5','tag6','tag7','tag8','tag9', 'skin_type1','skin_type2','skin_type3','skin_type4','skin_type5', 'product_type','skin_tone']]

    RS_pop_matrix = RS_pop.iloc[:, :-2]
    RS_pop_matrix = RS_pop_matrix.append(new_row, ignore_index= True)

    idx = RS_pop['product_idx'].copy()
    matrix = RS_pop.iloc[:,1:-2].copy()

    sim_data = cosine_similarity(matrix, matrix)
    sim = sim_data[-1]
    sim_rank = pd.DataFrame({'product_idx':idx,'sim':sim}).sort_values(by='sim', ascending =False)
    sim_rank = sim_rank.merge(RS_pop[['product_idx', 'product_type','skin_tone']], how='left', on='product_idx')[1:]

    # 유사 상품 10개
    score_data = score_data[['product_idx','color_score','detail_score1','detail_score2','detail_score3', 'weight']]
    score_data['weighted_score']  = weighted_score(score_data, selected_detail_score, w=0.5)
    score_data = score_data[['product_idx','weighted_score']]

    # 정렬된 유사 상품
    reco_rank = sim_rank.merge(score_data, how='left', on = 'product_idx')    
    
    return recommend(reco_rank, 3)


def contents_based(recommend_data, purchase_data, USER_ID, SKIN_TONE):
    ######################### db로 대체 #########################
    recommend_data = pd.read_csv("data/contents_based_all.csv")
    recommend_data.rename(columns = {'index':'product_idx', 'type':'product_type'}, inplace=True)
    #############################################################

    user_purchase_df = purchase_data[purchase_data.user_idx==USER_ID]
    RS_con = recommend_data[recommend_data['skin_tone'].str.contains(SKIN_TONE)]
    user_best_product = user_purchase_df.sort_values(by = 'processed_score', ascending = False).product_idx.values[0]

    idx = RS_con['product_idx']
    matrix = RS_con.drop(columns = ['product_idx','skin_tone','product_type'])
    sim_data = cosine_similarity(matrix, matrix)
    sim = sim_data[user_best_product]
    sim_rank = pd.DataFrame({'product_idx':idx,'sim':sim}).sort_values(by='sim', ascending =False)
    user_purchase_list = user_purchase_df.product_idx

    for purchase in user_purchase_list:
        if purchase in sim_rank['product_idx']:
            sim_rank = sim_rank[sim_rank['product_idx']!=purchase]

    reco_rank = sim_rank.merge(RS_con[['product_idx', 'product_type','skin_tone']], how='left', on='product_idx')[1:]

    return recommend(reco_rank, 3)


def collaborative(product_score_data, purchase_data, USER_ID, SKIN_TONE):
    ##########################################
    product_score_data = pd.read_csv("data/score_data.csv")
    product_score_data.rename(columns={'detail_socre1':'detail_score1','index':'product_idx','type':'product_type'}, inplace=True)
    ########################################
    SKIN_TONE = season(SKIN_TONE)
    RS_coll = pd.pivot_table(purchase_data, values='processed_score', index='user_idx', columns='product_idx', aggfunc='first')
    RS_coll['purchase_cnt'] = RS_coll.T.notnull().sum()
    RS_coll.loc['rating_cnt'] = RS_coll.notnull().sum()
    
    RS_coll = RS_coll[RS_coll['purchase_cnt'] >=10 ].drop(columns = 'purchase_cnt') ##
    RS_coll = RS_coll.T[RS_coll.loc['rating_cnt'] >=20 ].drop(columns = 'rating_cnt') ## 리뷰 수 20 이상 제품만
    RS_coll = RS_coll.T

    rating_matrix = RS_coll.fillna(0).copy()
    user_sim = cosine_similarity(rating_matrix, rating_matrix)
    user_sim_df = pd.DataFrame(user_sim, index = rating_matrix.index, columns = rating_matrix.index)
    sim_scores = user_sim_df[USER_ID].copy()
    sim_users = sim_scores.sort_values(ascending=False)[1:20].index 

    target_user_rating = rating_matrix.loc[USER_ID]
    target_user_rating = pd.DataFrame(target_user_rating[target_user_rating==0]) # 구매 상품 제외
    target_user_rating.columns = ['pred_rating']
    sim_users_df = rating_matrix.loc[sim_users]

    for prd in target_user_rating.index:
        prd_rating = sim_users_df[prd]
        prd_rating = prd_rating[prd_rating!=0]
        target_user_rating.loc[prd] = prd_rating.mean()
        
    target_user_rating = target_user_rating.sort_values(by = 'pred_rating', ascending=False)
    reco_rank = target_user_rating.merge(product_score_data[['skin_tone', 'product_type', 'product_idx']], how='left', on='product_idx')
    reco_rank = reco_rank.dropna(subset='product_type')

    reco_rank = reco_rank[reco_rank['skin_tone'].str.contains(SKIN_TONE)]

    return recommend(reco_rank, 3)