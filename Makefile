#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = Taxi_formula_revelation
PYTHON_VERSION = 3.10
PYTHON_INTERPRETER = python
DOCKER_IMAGE = dataminer_image
DOCKER_CONTAINER = dataminer_container
ENV_FILE = .env
MS_EDGE_USER_DATA_PATH = $(shell grep MS_EDGE_USER_DATA_PATH .env | cut -d '=' -f2)

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Set up python interpreter environment
.PHONY: create_environment
create_environment:
	
	conda create --name $(PROJECT_NAME) python=$(PYTHON_VERSION) --file requirements.txt -y

	@echo ">>> conda env created. Activate with:\nconda activate $(PROJECT_NAME)"

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	flake8 taxi
	isort --check --diff --profile black taxi
	black --check --config pyproject.toml taxi

## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml taxi

#################################################################################
# DOCKER SETUP AND USE                                                          #
#################################################################################

.PHONY : launch_datamining install_docker build_image run_container clean
launch_datamining: install_docker build_image run_container

install_docker:
	# Update package information
	sudo apt-get update
	# Install Docker prerequisites
	sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
	# Add Docker's GPG key
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	# Add Docker repository
	sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
	# Update package information again
	sudo apt-get update
	# Install Docker
	sudo apt-get install -y docker-ce

# Command to build the Docker image

build_image:
	docker build -t $(DOCKER_IMAGE) .

# Command to run the Docker container
run_container:
	docker run --env-file .env \
	-e DOCKER_ENV=true \
	--mount type=bind,source="$(MS_EDGE_USER_DATA_PATH)", \
	target=/app/MSEDGE_USER_DATA --name $(DOCKER_CONTAINER) $(DOCKER_IMAGE)

# Command to clean up (stop and remove container)
clean:
	docker stop $(DOCKER_CONTAINER)
	docker rm $(DOCKER_CONTAINER)

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
