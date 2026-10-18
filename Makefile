.PHONY: demo prepare train test api dashboard compose

demo:
	python scripts/generate_demo_data.py --patients 24 --days 75
	python scripts/prepare_data.py --input data/demo --horizons 24 48

prepare:
	python scripts/prepare_data.py --input data/raw/tihm --horizons 24 48

train:
	python scripts/train_models.py --dataset data/processed/healthguard_24h.csv --horizon 24

test:
	pytest -q

api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

dashboard:
	streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501

compose:
	docker compose up -d --build
