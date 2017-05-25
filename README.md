# PSI-Lab

PSI研究室レコメンドサービス

# http://compling.hss.ntu.edu.sg/wnja/data/1.1/wnjpn.db.gz


をmain.dbと同じ階層にダウンロードしてから利用してください！

・コンセプト

研究室探しを効率化



・必要なモジュール(DBにデータが入っていれば多分これだけのはず)

pip install Flask
<!-- pip install flask-mysqldb -->
<!-- pip install mecab-python3 -->



・起動方法等

ディレクトリに移動後以下のコマンドを叩くと，http://0.0.0.0:5000/ に起動
$ python main.py

http://0.0.0.0:5000/db でデータベースの中身を閲覧可能．



・注意点

入力欄は最大5個まで追加可能
