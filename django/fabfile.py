import time
from fabric.api import local, run, cd, env
from fabric.context_managers import warn_only


# COMMANDS #

def backup():
    # Backup database
    local('docker-compose exec postgres pg_dumpall -U postgres -c > ~/backup/dump`date +%d-%m-%Y`.sql')
    local('tar -czvf ~/backup/dump`date +%d-%m-%Y`.sql.tar.gz ~/backup/dump`date +%d-%m-%Y`.sql')
    # Backup media files
    local('tar -czvf ~/backup/dump`date +%d-%m-%Y`.media.tar.gz media/')


def tear_down():
    if 'tear_down' in env:
        env.tear_down()


def _drop_db():
    run('docker-compose exec postgres dropdb -U postgres postgres')


def _create_db():
    run('docker-compose exec postgres createdb -U postgres postgres')


def _backup_db():
    run('docker-compose exec postgres pg_dumpall -U postgres -c > ~/backup/dump`date +%d-%m-%Y`.sql')


def _restore_db():
    run('cat ~/backup/dump`date +%d-%m-%Y`.sql | docker exec -i $(docker-compose ps -q postgres) psql -Upostgres')
    # run('cat ../dump.json | docker exec -i tip_django_1 python manage.py loaddata_stdin')


def _migrate_db():
    run('docker-compose exec django python manage.py migrate --noinput')


def _import_geodata():
    run('python geodata_import.py')


def _update_translations_frontend():
    with warn_only():
        run("docker-compose exec django python manage.py update_translations master.pot")


def _update_translations_backend():
    with warn_only():
        run("docker-compose exec django django-admin makemessages -a")
        run("docker-compose exec django django-admin compilemessages")

# LOCAL STUFF #


def test(app=""):
    local("docker-compose exec django ptw -- {} -s --testmon".format(app))


def test_specific(specific_test=''):
    local(f"docker-compose exec django py.test -s -k {specific_test}")


def cov():
    local(
        "docker-compose exec django py.test --cov --cov-report html --cov-fail-under 100 --cov-report term-missing"
        " --cov-config .coveragerc"
    )


def lint():
    local('docker-compose exec django flake8')


def makemigrations():
    local('docker-compose exec django python manage.py makemigrations')


def migrate():
    local("docker-compose exec django python manage.py migrate --noinput")


def import_geodata():
    local("python geodata_import.py prod")


def rebuild_db():
    local("docker-compose exec postgres dropdb -U postgres postgres")
    local("docker-compose exec postgres createdb -U postgres postgres")
    local("cat ./dump.sql | docker exec -i $(docker-compose ps -q postgres) psql -Upostgres")


def add_base_db_data():
    """
    Adds basic data set to the db, like organizations, country and unicef offices
    """
    local("cat ./project/test-data/basic_data.sql | docker exec -i $(docker-compose ps -q postgres) psql -Upostgres")


def backup_db():
    local("docker-compose exec postgres pg_dumpall -U postgres -c > ./dump.sql")


def down():
    backup_db()
    local("docker-compose down")


def up():
    local("docker-compose up -d")


def up_debug():
    up()
    time.sleep(2)
    local("docker stop $(docker-compose ps -q django)")
    local("docker-compose run --service-ports django python manage.py runserver 0.0.0.0:8000")


def update_translations():
    local("docker-compose exec django python manage.py update_translations master.pot")


def shell():
    local("docker-compose exec django python manage.py shell")


def log():
    local("docker-compose logs -f django")


def single_coverage(folder, test_to_run):
    local("touch .lcoveragerc")
    local("printf '[run]\nsource = {}' > .lcoveragerc".format(folder))
    local("docker-compose exec django py.test --cov --cov-report term-missing -k"
          " '{}' --cov-config .lcoveragerc".format(test_to_run))


def send_test_email(type, email, **kwargs):
    params = ""
    for key, value in kwargs.items():
        params += '--{} {} '.format(key, value)
    local("docker-compose exec django python manage.py send_html_email {} {} {}".format(type, email, params) +
          "--settings=tiip.settings_email_test")


def dump_model_translations():
    local("docker-compose exec django python manage.py dumpdata country.country > Country.json")
    local("docker-compose exec django python manage.py dumpdata project.digitalstrategy > DigitalStrategy.json")
    local("docker-compose exec django python manage.py dumpdata project.healthcategory > HealthCategory.json")
    local("docker-compose exec django python manage.py dumpdata project.healthfocusarea > HealthFocusArea.json")
    local("docker-compose exec django python manage.py dumpdata project.hisbucket > HISBucket.json")
    local("docker-compose exec django python manage.py dumpdata project.hscchallenge > HSCChallenge.json")
    local("docker-compose exec django python manage.py dumpdata project.hscgroup > HSCGroup.json")
    local(
        "docker-compose exec django python manage.py dumpdata project.interoperabilitylink > InteroperabilityLink.json")
    local(
        "docker-compose exec django python manage.py dumpdata "
        "project.interoperabilitystandard > InteroperabilityStandard.json")
    local("docker-compose exec django python manage.py dumpdata project.licence > Licence.json")
    local("docker-compose exec django python manage.py dumpdata project.technologyplatform > TechnologyPlatform.json")
    local("tar -czvf translation_dumps_`date +%d-%m-%Y`.tar.gz *.json")
    local("rm *.json")
