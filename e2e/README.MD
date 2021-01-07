# Installation
## Installing requirements
### Linux
`sudo apt update && sudo apt install yarn`
### macOS
(to be done)
### Windows
(to be done)
## Installing cypress
### Linux
`yarn add cypress --dev`
`npx cypress open` - ???
### macOS
(to be done)
### Windows
(to be done)
# Running
## Running requirements
in repository root dir: `docker-compose up` (with `-d` optional parameter for running in daemon mode)
in frontend directory: `yarn dev`
# Running in GUI mode
in e2e dir: `yarn exec cypress open`
# Running the tests through Docker`
in e2e dir: `docker run -it -v $PWD:/e2e -w /e2e cypress/included:6.2.1`
