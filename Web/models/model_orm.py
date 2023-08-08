# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# # from app import db

# db_config = {
#     'dbname': 'database_name',
#     'user': 'database_user',
#     'password': 'database_password',
#     'host': 'database_host',
#     'port': 'database_port',
# }

# # 엔진 생성
# engine = create_engine(f'postgresql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["dbname"]}')
# Base = declarative_base(bind=engine)
# Session = sessionmaker(bind=engine)


# # 테이블 모델 정의
# class Table1(Base):
#     __tablename__ = 'lib'


# class Table2(Base):
#     __tablename__ = 'eyeshadow'

# class Table3(Base):
#     __tablename__ = 'brush'
    