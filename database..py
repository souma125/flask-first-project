from sqlalchemy import create_engine,text
engine = create_engine("mysql+pymysql://root:@localhost/parineetas_career?charset=utf8mb4")
with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM `jobs`"))
    for row in result:
        print("title:", row.title)