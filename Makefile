SPARK := docker compose exec -T spark
COMPOSE := docker compose

.DEFAULT_GOAL := help

help:
	@echo "make setup     build the image, start the container, generate the dataset"
	@echo "make rollup    run the Part A job"
	@echo "make verify    check Part A output against the reference"
	@echo "make drops     print a few sample records from the daily drops"
	@echo "make test      pytest"
	@echo "make shell     a shell inside the container"
	@echo "make down      stop the container"
	@echo "make clean     stop and delete all generated data"

setup:
	$(COMPOSE) up -d --build
	@echo "waiting for container..."
	@until $(COMPOSE) exec -T spark true 2>/dev/null; do sleep 1; done
	$(SPARK) python3 scripts/generate_data.py
	@echo ""
	@echo "ready. next: time your baseline with  make rollup"

rollup:
	$(SPARK) spark-submit jobs/daily_rollup.py

verify:
	$(SPARK) spark-submit scripts/verify.py

write-reference:
	$(SPARK) spark-submit scripts/verify.py --write-reference

drops:
	@$(SPARK) python3 -c "import json,itertools; \
f=open('data/drops/day_4.json'); \
[print(json.dumps(json.loads(l), indent=2)) for l in itertools.islice(f,3)]"

test:
	$(SPARK) python3 -m pytest tests/ -q

shell:
	$(COMPOSE) exec spark bash

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v
	rm -rf data/generated data/drops out

.PHONY: help setup rollup verify write-reference drops test shell down clean
