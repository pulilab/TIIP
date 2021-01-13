# Installation
## Installing requirements
This is only required for running the GUI mode locally, for running in the console, we've a docker compose configuration available.
### Linux
`sudo apt update && sudo apt install yarn`
### macOS
(to be done)
### Windows
(to be done)
## Installing cypress
### Linux
`yarn add cypress --dev`
`npx cypress open` - to set up cypress's local variables
### macOS
(to be done)
### Windows
(to be done)
# Running
## Running requirements
in repository root dir: `docker-compose -f docker-compose.yml -f docker-compose.e2e.yml up -d` (with `-d` optional parameter for running in daemon mode)
This command starts up all of our docker containers, with `http://localhost/` as the root url.
# Running in GUI mode
## Configuration
in e2e dir: `yarn exec cypress open`
# Running the tests through Docker`
in e2e dir: `docker run --network host -it -v $PWD:/e2e -w /e2e cypress/included:6.2.1`
This command starts up a premade Cypress container and runs the test sets using the host computer's network settings.
# Good to know
- `cypress.json` and `cypress.dev.json` contain the configuration files for Cypress
