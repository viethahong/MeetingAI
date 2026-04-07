install:
	uv sync

run:
	uv run meetingai $(ARGS)

ui:
	uv run meetingai-ui

docker:
	docker compose up --build

test:
	uv run pytest
