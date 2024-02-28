# TL;DR
slackの文章を記録し、表示するwebアプリを作成する

<br>

# 前提の環境
詳細は環境構築へ
* Ubuntu20(推奨，下3つがあれば多分大丈夫)
* Docker(rootlessでない)
* docker-compose
* make
* MySQL

<br>

# 各コンテナの説明
## slack_bot
slackを監視して、DBに蓄積していく

## run_html
個人用PCから状態を確認できるように8080ポートで解放する．
`\\<サーバーのIPアドレス>:8080`でアクセスできる．

## run_mysql
slack_botで得た値を保存する．

データベースはこのディレクトリの"`./mysql/db`"に保存される．[docker-compose.yml](docker-compose.yml)の`./mysql/db:/var/lib/mysql`でマウント先を変えることも可能．
dockerがsudo権限で動いているため，ファイルアクセスにはsudo権限が必要(mysqlはsudo権限で動いているため，mysqlには普通にアクセス可能)


<br>

# 環境構築
## Dockerのインストール
macやwindowsの場合はDocker Desktopが入ってればok

linuxの場合
https://docs.docker.com/install/linux/docker-ce/ubuntu/ に書いてあり通りにやる
```
sudo docker run hello-world
```
これができればok

## docker-composeのインストール
参考
https://docs.docker.jp/compose/install.html#linux
```
sudo curl -L https://github.com/docker/compose/releases/download/<バージョン>/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```
`<バージョン>`は[GitHub](https://github.com/docker/compose/releases)を見て最新のものにしておくこと


## makeのインストール
```
sudo apt install make
```
長いコマンドを`make ~~`出かけるようになる．`makefile`に詳細が記述されている．

<br>

# もろもろのコマンド

## イメージのビルド，コンテナの立ち上げ，実行
```
make start
```
初回はイメージの作成が走る．
2回目以降は作成が走らずにコンテナが建つ．

## コンテナの終了
```
make stop
```

## コンテナの再実行
```
make restart
```

## コンテナ，dockerネットワークの削除
```
make rm
```

## 起動コンテナ確認
```
make ps
```

## イメージの削除
```
make rmi
```

## 全削除
状態にもよるが以下の順で初期状態にできる．始めるときはまた`make start`から．
たまに関連コンテナやイメージが存在し削除できないと言われるので，その場合は個々に`sudo docker container rm ~~`や`sudo docker rmi ~~`で削除する
```
make stop
make rm
make rmi
```

## イメージのビルドしなおし
`make start`だと以前のキャッシュを使ってしまうが，こちらはキャッシュを使わずに1からビルドする．
ただしコンテナの起動はされないので，改めて`make start`する必要がある．
```
make build
```

## api_keys.py
以下のファイルを作成し、記述する
tokenの取得は調べてください

```
SLACK_API_TOKEN = "xapp ..."
SLACK_BOT_USER_TOKEN = "xoxb ..."
```

<!--
# TODO
- [x] MySQLをDockerコンテナにする
- [x] ユーザーログインを管理者にする（パスワードはべた書きでいい）
- [x] イメージをコマンド一発でビルドできるように
- [x] docker-composeと通常のDockerのインストール方法を書く
- [x] Gmailの2段階認証パスワードについて
- [x] localhostでできなさそう→コンテナ同氏はdocker networkでつながるのでゲートウェイを指定してやれば行けた
 -->
