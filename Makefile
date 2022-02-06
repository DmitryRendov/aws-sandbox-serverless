SHELL := /bin/bash -o pipefail -o errexit

# Directory for all the build artefacts to be archived by CI.
artefacts_path := artefacts
# Env vars
CONDA_ENV_FILE = environment.yml
REQUIREMENTS_FILE = src/web/requirements.txt
ENVNAME := aws-sandbox-serverless$(RANDOM_SUFFIX)


define print_status_noprc
	@echo "############################################"; \
	echo "#"; \
	echo "#    "$(1); \
	echo "#"; \
	echo "############################################"
	@mkdir -p $(artefacts_path)
	@echo "$$(date +%Y-%m-%dT%H:%M:%S%z): $(1)" >> $(artefacts_path)/make.log
endef


###################################### Operation and helper targets ##########################################

conda-setup:
	$(call print_status_noprc,Setup conda)
	ACTIVATE=$(TEST_CONDA_LOCATION)/bin/activate; \
	if [ ! -f "$$ACTIVATE" ]; then \
		wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh; \
		bash miniconda.sh -b -p $(TEST_CONDA_LOCATION); \
		rm miniconda.sh; \
		source "$$ACTIVATE"; \
		conda update -y conda; \
	else \
		echo "Speeding up"; \
		source "$$ACTIVATE"; \
	fi; \
	# Useful for debugging any conda issues; \
	# conda info -a

environment:
	$(call print_status_noprc,Creating conda $(ENVNAME) environment)
	conda config --set always_yes yes --set changeps1 no; \
	conda env create --name $(ENVNAME) --file .ci/$(CONDA_ENV_FILE) --force

get-requirements:
	$(call print_status_noprc,Creating $(REQUIREMENTS_FILE) from conda $(ENVNAME) environment)
	pip list --format=freeze > $(REQUIREMENTS_FILE)

test-lints:
	$(call print_status_noprc,Linting Python code with pylint/flake8)
	@pylint --rcfile=.ci/pylintrc --output-format=parseable src/* 2>&1 | tee $(artefacts_path)/pylint.log || true; \
	flake8 --config=.ci/flake8rc src/* 2>&1 | tee $(artefacts_path)/flake8.log

style:
	$(call print_status_noprc,Styling with black)
	find src -type f -name "*.py" -print0 | xargs -0r black
