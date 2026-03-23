test:
	pytest app/tests -q

build:
	docker build -t payments-api:local -f Dockerfile .
	docker build -t payments-blockchain:local -f Dockerfile.blockchain .

smoke:
	chmod +x scripts/post_deploy_test.sh && ./scripts/post_deploy_test.sh
