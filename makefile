start:
	docker-compose up -d
stop:
	docker-compose stop
restart:
	docker-compose restart
rm:
	docker-compose rm && make rmnetwork
rmi:
	docker rmi slack_bot run_html mysql
ps:
	docker-compose ps
rmnetwork:
	docker network rm lab_message_app_mynet
build:
	docker-compose build --no-cache
reboot:
	make stop && docker-compose rm -f && docker network rm lab_message_app_mynet && make start