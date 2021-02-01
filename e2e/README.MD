# End to end testing
## Installation
This is only required for running the GUI mode locally, for running in the console, we've a docker compose configuration available.
## Pre-requirements
Install [node]() if you don't have it. Then, on you prefer terminal:

```bash
# be sure to be inside e2e folder

# linux
$ sudo apt update && sudo apt install yarn
$ yarn add cypress --dev
$ yarn test:dev
# or
$ yarn test:pro

# macOS
$ npm install -g yarn
$ yarn
$ yarn test:dev
# or
$ yarn test:pro
```
## Running

On your terminal, type:

```bash
# in root directory from project
# with `-d` optional parameter for running in daemon mode
$ docker-compose -f docker-compose.yml -f docker-compose.e2e.yml up -d
```

This command start up all of our docker containers, with `http://localhost/` as the root url.

## GUI mode

To open the GUI for end to end testing, in your terminal, go to the `e2e/` folder and:

```bash
$ yarn test:dev
# or
$ yarn test:pro
```
## Docker e2e test run

Go `e2e/` folder: 

```bash
$ docker run --network host -it -v $PWD:/e2e -w /e2e cypress/included:6.2.1
```
This command starts up a premade *Cypress* container and runs the test sets using the host computer's network settings.
## FAQ

- Need to change configuration of test? `cypress.json` and `cypress.dev.json` contain the configuration files for Cypress.
