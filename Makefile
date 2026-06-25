.PHONY: manifest list validate test-smoke help

help:
	@echo "OpenAI-RLHF tooling"
	@echo "  make manifest     Generate TASKS.json"
	@echo "  make list         List Months tasks with tests"
	@echo "  make validate     Validate repository structure"
	@echo "  make test-smoke   Run Month7 smoke tests (few deps)"

manifest:
	python3 scripts/generate_task_manifest.py

list:
	python3 scripts/list_tasks.py --track months --has-tests

validate:
	python3 scripts/validate_repo.py

test-smoke:
	python3 scripts/run_tests.py --month Month7 --limit 5
