import copy
import random
import mock
import pytz

from datetime import datetime, timedelta

from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from django.core import mail
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APIClient

from country.models import Country, Donor
from project.admin import ProjectAdmin
from project.utils import get_temp_image
from user.models import Organisation, UserProfile
from project.models import Project, DigitalStrategy, TechnologyPlatform, \
    HSCChallenge, HSCGroup, ProjectApproval, Stage
from project.tasks import send_project_approval_digest, notify_superusers_about_new_pending_approval, \
    notify_user_about_approval

from project.tests.setup import SetupTests, MockRequest
from user.tests import create_profile_for_user


class ProjectTests(SetupTests):
    def test_retrieve_project_structure(self):
        url = reverse("get-project-structure")
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "technology_platforms")
        self.assertContains(response, "hsc_challenges")
        self.assertEqual(len(response.json().keys()), 22)

    def test_retrieve_project_structure_cache(self):
        with self.settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}):
            cache.clear()
            # Shouldn't exists
            cache_data = cache.get('project-structure-data')
            self.assertTrue(cache_data is None)

            # First time retrieval should create cache data
            url = reverse("get-project-structure")
            response = self.test_user_client.get(url)
            cache_data = cache.get('project-structure-data-en')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(cache_data is None)

            # Changing cached data should invalidate cache
            st = Stage.objects.all().first()
            st.name = 'other'
            st.save()
            cache_data = cache.get('project-structure-data')
            self.assertTrue(cache_data is None)

            # Retrieval should create cache data again
            url = reverse("get-project-structure")
            response = self.test_user_client.get(url)
            cache_data = cache.get('project-structure-data-en')
            self.assertEqual(response.status_code, 200)
            self.assertFalse(cache_data is None)

    def test_create_new_project_approval_required(self):
        c = Country.objects.get(id=self.country_id)
        c.project_approval = True
        c.users.add(self.user_profile_id)
        c.save()
        url = reverse("project-create", kwargs={"country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(dict(name="Test Project3"))
        response = self.test_user_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProjectApproval.objects.filter(project_id=response.data['id']).exists(), True)

    def test_create_new_project_approval_required_on_update(self):
        # Make country approval-required
        c = Country.objects.get(id=self.country_id)
        c.project_approval = True
        c.users.add(self.user_profile_id)
        c.save()
        # Create project
        url = reverse("project-create", kwargs={"country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(dict(name="Test Project3"))
        response = self.test_user_client.post(url, data, format="json")
        project_id = response.data['id']
        approval = ProjectApproval.objects.filter(project_id=response.data['id']).first()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(approval)
        # Approve project
        approval.approved = True
        approval.save()
        # Update project
        url = reverse("project-publish", kwargs={"project_id": project_id, "country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(dict(name="Test Project updated"))
        response = self.test_user_client.put(url, data, format="json")
        new_approval = ProjectApproval.objects.filter(project_id=response.data['id']).first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_approval.approved, None)

    def test_project_approval_project_methods(self):
        project = Project.objects.get(id=self.project_id)
        project.approve()

        approval = ProjectApproval.objects.get(project_id=self.project_id)

        self.assertTrue(project.approval.approved)
        self.assertTrue(approval.approved)

        project.disapprove()
        approval.refresh_from_db()

        self.assertFalse(project.approval.approved)
        self.assertFalse(approval.approved)

        project.reset_approval()
        approval.refresh_from_db()

        self.assertIsNone(project.approval.approved)
        self.assertIsNone(approval.approved)

        self.assertEqual(approval.__str__(), 'Approval for {}'.format(project.name))

    def test_project_approval_list_by_country(self):
        url = reverse("approval", kwargs={"country_id": self.country_id})
        response = self.test_user_client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['project_name'], self.project_data['project']['name'])
        self.assertEqual(response.json()[0]['history'][0]['history_user__userprofile'], self.user_profile_id)
        self.assertIsNone(response.json()[0]['history'][0]['approved'])
        self.assertIsNone(response.json()[0]['history'][0]['reason'])

    def test_project_approval_approve(self):
        project = Project.objects.get(id=self.project_id)
        approval = project.approval

        url = reverse("approval", kwargs={"pk": approval.id})
        response = self.test_user_client.put(url, data={}, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'detail': 'You do not have permission to perform this action.'})

        self.country.admins.add(self.user_profile_id)
        url = reverse("approval", kwargs={"pk": approval.id})
        response = self.test_user_client.put(url, data={'approved': True, 'reason': 'all good'}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['history']), 2)
        self.assertTrue(response.json()['history'][0]['approved'], self.user_profile_id)
        self.assertEqual(response.json()['history'][0]['reason'], 'all good')

    def test_create_validating_list_fields_invalid_data(self):
        url = reverse("project-create", kwargs={"country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(dict(
            name="Test Project4",
            health_focus_areas=[{"object": "not good"}],
            donors=[{"object": "not good"}],
            hsc_challenges=[{"object": "not good"}],
        ))
        response = self.test_user_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.json()['project'].keys()), 3)
        self.assertEqual(response.json()['project']['health_focus_areas']['0'], ['A valid integer is required.'])
        self.assertEqual(response.json()['project']['donors']['0'], ['A valid integer is required.'])
        self.assertEqual(response.json()['project']['hsc_challenges']['0'], ['A valid integer is required.'])

    def test_publish_project_makes_public_id(self):
        url = reverse("project-create", kwargs={"country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(name="Test Project4")
        response = self.test_user_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.json()['public_id'])
        project_id = response.json()['id']

        url = reverse("project-publish", kwargs={"project_id": project_id, "country_office_id": self.country_office.id})
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['public_id'])

        url = reverse("project-retrieve", kwargs={"pk": project_id})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['public_id'])

    def test_update_project(self):
        url = reverse("project-publish",
                      kwargs={"project_id": self.project_id, "country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(name="TestProject98",
                               platforms=[999], dhis=[998])
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['published']["platforms"], [999])
        self.assertEqual(response.json()['published']["dhis"], [998])

    def test_project_data_missing(self):
        data = copy.deepcopy(self.project_data)
        data.pop('project', None)

        url = reverse("project-publish", kwargs={"project_id": self.project_id,
                                                 "country_office_id": self.country_office.id})
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'project': 'Project data is missing'})

        url = reverse("project-draft", kwargs={"project_id": self.project_id,
                                               "country_office_id": self.country_office.id})
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'project': 'Project data is missing'})

        url = reverse("project-create", kwargs={"country_office_id": self.country_office.id})
        response = self.test_user_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'project': 'Project data is missing'})

    def test_create_new_project_unique_name(self):
        url = reverse("project-create", kwargs={"country_office_id": self.country_office.id})
        response = self.test_user_client.post(url, self.project_data, format="json")
        self.assertEqual(response.status_code, 201)
        project_id = response.json()['id']
        self.assertEqual(response.json()['draft']['name'], self.project_data['project']['name'])

        url = reverse("project-publish", kwargs={"project_id": project_id,
                                                 "country_office_id": self.country_office.id})
        response = self.test_user_client.put(url, self.project_data, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['project']['name'][0], 'This field must be unique.')

    def test_retrieve_project(self):
        url = reverse("project-retrieve", kwargs={"pk": self.project_id})
        response = self.test_user_client.get(url, HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['published'].get("name"), "Test Project1")
        self.assertEqual(response.json()['published'].get("platforms")[0],
                         self.project_data['project'].get("platforms")[0])
        self.assertEqual(response.json()['published'].get("country"), self.country_id)

        response = self.test_user_client.get(url, HTTP_ACCEPT_LANGUAGE='fr')
        self.assertEqual(response.status_code, 200)

    def test_retrieve_wrong_http_command(self):
        url = reverse("project-retrieve", kwargs={"pk": self.project_id})
        response = self.test_user_client.put(url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {'detail': 'Method "PUT" not allowed.'})

    def test_retrieve_project_list(self):
        url = reverse("project-list", kwargs={'list_name': 'member-of'})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'][0]['published'].get("name"), "Test Project1")

    def test_make_version(self):
        url = reverse("make-version", kwargs={"project_id": self.project_id})
        response = self.test_user_client.post(url, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn('coverage', response.json())
        self.assertIn('toolkit', response.json())
        self.assertIn('last_version', response.json()['coverage'])
        self.assertIn('last_version_date', response.json()['coverage'])
        self.assertIn('last_version', response.json()['toolkit'])
        self.assertIn('last_version_date', response.json()['toolkit'])

    def test_make_version_wrong_id(self):
        url = reverse("make-version", kwargs={"project_id": 999})
        response = self.test_user_client.post(url, format="json")
        self.assertEqual(response.status_code, 400)

    def test_get_toolkit_versions(self):
        url = reverse("make-version", kwargs={"project_id": self.project_id})
        self.test_user_client.post(url, format="json")
        url = reverse("get-toolkit-versions", kwargs={"project_id": self.project_id})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_version_numbers_increasing(self):
        url = reverse("make-version", kwargs={"project_id": self.project_id})
        self.test_user_client.post(url, format="json")
        self.test_user_client.post(url, format="json")
        url = reverse("get-toolkit-versions", kwargs={"project_id": self.project_id})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[1]["version"], 2)

    def test_retrieve_last_version(self):
        url = reverse("make-version", kwargs={"project_id": self.project_id})
        self.test_user_client.post(url, format="json")
        url = reverse("project-retrieve", kwargs={"pk": self.project_id})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['published'].get("name"), "Test Project1")
        self.assertEqual(response.json()['published'].get("last_version"), 1)
        self.assertIn("last_version_date", response.json()['published'])

    def test_create_project_adds_owner_to_team(self):
        url = reverse("project-create", kwargs={"country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(name="Test Project3")
        response = self.test_user_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)

        userprofile = UserProfile.objects.get(name="Test Name")
        project = Project.objects.get(id=response.json()['id'])
        self.assertEqual(project.team.first(), userprofile)

    def test_team_cant_be_but_viewers_can_be_empty(self):
        url = reverse("project-create", kwargs={"country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(name="Test Project4")
        response = self.test_user_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)

        userprofile = UserProfile.objects.get(name="Test Name")
        project = Project.objects.get(id=response.json()['id'])
        self.assertEqual(project.team.first(), userprofile)

        url = reverse("project-groups", kwargs={"pk": project.id})

        groups = {
            "team": [userprofile.id],
            "viewers": [userprofile.id]
        }

        response = self.test_user_client.put(url, groups)
        self.assertTrue("team" in response.json())
        self.assertTrue("viewers" in response.json())
        self.assertEqual(response.json()['team'], [userprofile.id])
        self.assertEqual(response.json()['viewers'], [userprofile.id])

        url = reverse("project-groups", kwargs={"pk": project.id})

        groups = {
            "team": [],
            "viewers": []
        }
        response = self.test_user_client.put(url, groups)

        self.assertTrue("team" in response.json())
        self.assertTrue("viewers" in response.json())
        self.assertEqual(response.json()['team'], [userprofile.id])
        self.assertEqual(response.json()['viewers'], [])

    def test_by_user_manager(self):
        url = reverse("project-list", kwargs={'list_name': 'member-of'})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'][0]['published']['name'], "Test Project1")

    def test_project_group_list_team(self):
        url = reverse("project-groups", kwargs={"pk": self.project_id})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['team'][0], self.user_profile_id)

    def test_project_group_add_user_to_team(self):
        # Create a test user with profile.
        url = reverse("rest_register")
        data = {
            "email": "test_user2@gmail.com",
            "password1": "123456hetNYOLC",
            "password2": "123456hetNYOLC"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        create_profile_for_user(response)

        # Log in the user.
        url = reverse("api_token_auth")
        data = {
            "username": "test_user2@gmail.com",
            "password": "123456hetNYOLC"}
        response = self.client.post(url, data)
        test_user_key = response.json().get("token")
        test_user_client = APIClient(HTTP_AUTHORIZATION="Token {}".format(test_user_key), format="json")
        user_profile_id = response.json().get("user_profile_id")

        # update profile.
        org = Organisation.objects.create(name="org2")
        url = reverse("userprofile-detail", kwargs={"pk": user_profile_id})
        data = {
            "name": "Test Name 2",
            "organisation": org.id,
            "country": self.country_id}
        response = test_user_client.put(url, data, format="json")

        user_profile_id = response.json()['id']

        url = reverse("project-groups", kwargs={"pk": self.project_id})

        groups = {
            "team": [user_profile_id],
            "viewers": []
        }
        response = self.test_user_client.put(url, groups, format="json")

        self.assertTrue("team" in response.json())
        self.assertTrue("viewers" in response.json())
        self.assertEqual(response.json()['team'], [user_profile_id])

        url = reverse("project-groups", kwargs={"pk": self.project_id})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['team'][0], user_profile_id)

    def test_project_group_add_user_always_overwrites_all_groups(self):
        url = reverse("project-groups", kwargs={"pk": self.project_id})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        owner_id = response.json()['team'][0]

        # Create a test user with profile.
        url = reverse("rest_register")
        data = {
            "email": "test_user2@gmail.com",
            "password1": "123456hetNYOLC",
            "password2": "123456hetNYOLC"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        create_profile_for_user(response)

        # Log in the user.
        url = reverse("api_token_auth")
        data = {
            "username": "test_user2@gmail.com",
            "password": "123456hetNYOLC"}
        response = self.client.post(url, data)
        test_user_key = response.json().get("token")
        test_user_client = APIClient(HTTP_AUTHORIZATION="Token {}".format(test_user_key), format="json")
        user_profile_id = response.json().get('user_profile_id')

        # update profile.
        org = Organisation.objects.create(name="org2")
        url = reverse("userprofile-detail", kwargs={"pk": user_profile_id})
        data = {
            "name": "Test Name 2",
            "organisation": org.id,
            "country": self.country_id}
        response = test_user_client.put(url, data, format="json")

        user_profile_id = response.json()['id']

        url = reverse("project-groups", kwargs={"pk": self.project_id})

        groups = {
            "team": [user_profile_id],
            "viewers": []
        }
        response = self.test_user_client.put(url, groups, format="json")

        self.assertTrue("team" in response.json())
        self.assertTrue("viewers" in response.json())
        self.assertTrue(owner_id not in response.json()['team'])
        self.assertEqual(response.json()['team'], [user_profile_id])

    def test_update_project_updates_health_focus_areas(self):
        retrieve_url = reverse("project-retrieve", kwargs={"pk": self.project_id})
        response = self.test_user_client.get(retrieve_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['published'].get('health_focus_areas'),
                         self.project_data['project']['health_focus_areas'])

        data = copy.deepcopy(self.project_data)
        data['project'].update(health_focus_areas=[1])
        url = reverse("project-publish", kwargs={"project_id": self.project_id,
                                                 "country_office_id": self.country_office.id})
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['published']["health_focus_areas"], data['project']['health_focus_areas'])
        self.assertNotEqual(response.json()['published']["health_focus_areas"],
                            self.project_data['project']['health_focus_areas'])

        response = self.test_user_client.get(retrieve_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['published'].get('health_focus_areas'), data['project']['health_focus_areas'])
        self.assertNotEqual(response.json()['published'].get('health_focus_areas'),
                            self.project_data['project']['health_focus_areas'])

    def test_update_project_with_different_invalid_name(self):
        url = reverse("project-publish", kwargs={"project_id": self.project_id,
                                                 "country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(
            name="toolongnamemorethan128charactersisaninvalidnameheretoolongnamemorethan128charactersisaninv"
                 "alidnameheretoolongnamemorethan128charactersisaninvalidnamehere")
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['project']["name"][0], 'Ensure this field has no more than 128 characters.')

    def test_update_project_with_new_name_that_collides_with_a_different_project(self):
        url = reverse("project-create", kwargs={"country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(name="thisnameisunique")
        response = self.test_user_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        project_id = response.json()['id']

        url = reverse("project-publish", kwargs={"project_id": project_id,
                                                 "country_office_id": self.country_office.id})
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 2)

        url = reverse("project-publish", kwargs={"project_id": self.project_id,
                                                 "country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        data['project'].update(name="thisnameisunique")
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['project']["name"][0], 'This field must be unique.')

    def test_digitalstrategies_str(self):
        ds1 = DigitalStrategy.objects.create(name='ds1', group='Client')
        ds2 = DigitalStrategy.objects.create(name='ds2', group='Client', parent=ds1)
        self.assertEqual(str(ds1), '[Client] ds1')
        self.assertEqual(str(ds2), '[Client] [ds1] ds2')

    def test_platforms_str(self):
        tp = TechnologyPlatform.objects.create(name='tp')
        self.assertEqual(str(tp), 'tp')

    def test_hsc_str(self):
        hsc_group = HSCGroup.objects.create(name='name')
        item = HSCChallenge.objects.create(name='challenge', group=hsc_group)
        self.assertEqual(str(item), '(name) challenge')

    def test_project_admin_link_add(self):
        request = MockRequest()
        site = AdminSite()
        user = UserProfile.objects.get(id=self.user_profile_id).user
        request.user = user
        pa = ProjectAdmin(Project, site)
        link = pa.link(Project())
        self.assertEqual(link, '-')

    def test_project_admin_link_edit(self):
        request = MockRequest()
        site = AdminSite()
        user = UserProfile.objects.get(id=self.user_profile_id).user
        request.user = user
        pa = ProjectAdmin(Project, site)
        p = Project.objects.create(name="test link")
        link = pa.link(p)

        expected_link = f"<a target='_blank' href='/en/-/initiatives/{p.id}/edit/'>Edit initiative</a>"
        self.assertEqual(link, expected_link)

    def test_project_approval_email(self):
        user_2 = User.objects.create_superuser(username='test_2', email='test2@test.test', password='a')
        user_2_profile = UserProfile.objects.create(user=user_2, language='fr')

        c = Country.objects.get(id=self.country_id)
        c.project_approval = True
        c.users.add(self.user_profile_id, user_2_profile)
        c.save()
        send_project_approval_digest()

        first_en = '<meta http-equiv="content-language" content="en">' in mail.outbox[-2].message().as_string()
        en_index = -2 if first_en else -1
        fr_index = -1 if first_en else -2

        outgoing_en_email_text = mail.outbox[en_index].message().as_string()
        self.assertIn('/en/-/admin/country', outgoing_en_email_text)
        self.assertIn('<meta http-equiv="content-language" content="en">', outgoing_en_email_text)

        outgoing_fr_email_text = mail.outbox[fr_index].message().as_string()
        self.assertIn('/fr/-/admin/country', outgoing_fr_email_text)
        self.assertIn('<meta http-equiv="content-language" content="fr">', outgoing_fr_email_text)

    def test_project_approval_email_not_sent(self):
        pa = Project.objects.get(id=self.project_id).approval
        pa.approved = True
        pa.save()
        send_project_approval_digest()
        self.assertEqual(len(mail.outbox), 0)

    def test_country_admins_access_all_projects_in_country_as_viewer(self):
        # Create a test user with profile.
        url = reverse("rest_register")
        data = {
            "email": "test_user2@gmail.com",
            "password1": "123456hetNYOLC",
            "password2": "123456hetNYOLC"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        create_profile_for_user(response)

        # Log in the user.
        url = reverse("api_token_auth")
        data = {
            "username": "test_user2@gmail.com",
            "password": "123456hetNYOLC"}
        response = self.client.post(url, data, format="json")
        test_user_key = response.json().get("token")
        test_user_client = APIClient(HTTP_AUTHORIZATION="Token {}".format(test_user_key), format="json")
        user_profile_id = response.json().get('user_profile_id')

        # update profile.
        org = Organisation.objects.create(name="org2")
        url = reverse("userprofile-detail", kwargs={"pk": user_profile_id})
        data = {
            "name": "Test Name 2",
            "organisation": org.id,
            "country": "test_country"}
        test_user_client.put(url, data, format="json")

        project_id, project_data, org, country, country_office, d1, d2 = self.create_new_project()

        p_in_country = Project.objects.get(id=project_id)
        p_not_in_country = Project.objects.get(name="Test Project1")

        # make user country admin of CTR2
        country.users.add(self.user_profile_id)
        # make sure he is not a country admin of project 1's country
        p_not_in_country.get_country().users.remove(self.user_profile_id)

        # remove this user from all the projects
        for p in Project.objects.all():
            p.team.remove(self.user_profile_id)
            p.team.add(user_profile_id)

            # this user doesn't belong to any project anymore
            self.assertFalse(p.team.filter(id=self.user_profile_id).exists())
            self.assertFalse(p.viewers.filter(id=self.user_profile_id).exists())

            # the project belongs to the new user now
            self.assertTrue(p.team.filter(id=user_profile_id).exists())

        url = reverse("project-retrieve", kwargs={"pk": p_in_country.id})
        response = self.test_user_client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()['published']['start_date'], str)
        self.assertEqual(response.json()['draft']['name'], p_in_country.name)

        url = reverse("project-retrieve", kwargs={"pk": p_not_in_country.id})
        response = self.test_user_client.get(url, format="json")
        self.assertIsNone(response.json()['draft'])
        self.assertTrue('start_date' not in response.json()['published'])

        # Only works for retrieve, the list won't list any project that are not his/her
        url = reverse("project-list", kwargs={'list_name': 'member-of'})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    def test_admins_access_all_projects_as_viewer(self):
        # Create a test user with profile.
        url = reverse("rest_register")
        data = {
            "email": "test_user2@gmail.com",
            "password1": "123456hetNYOLC",
            "password2": "123456hetNYOLC"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        create_profile_for_user(response)

        # Log in the user.
        url = reverse("api_token_auth")
        data = {
            "username": "test_user2@gmail.com",
            "password": "123456hetNYOLC"}
        response = self.client.post(url, data, format="json")
        test_user_key = response.json().get("token")
        test_user_client = APIClient(HTTP_AUTHORIZATION="Token {}".format(test_user_key), format="json")
        user_profile_id = response.json().get('user_profile_id')

        # update profile.
        org = Organisation.objects.create(name="org2")
        url = reverse("userprofile-detail", kwargs={"pk": user_profile_id})
        data = {
            "name": "Test Name 2",
            "organisation": org.id,
            "country": "test_country"}
        test_user_client.put(url, data, format="json")

        project_id, project_data, org, country, country_office, d1, d2 = self.create_new_project()

        p_in_country = Project.objects.get(id=project_id)
        p_not_in_country = Project.objects.get(name="Test Project1")

        # make sure he is not a country admin of project 1 or 2's country
        p_in_country.get_country().users.remove(self.user_profile_id)
        p_not_in_country.get_country().users.remove(self.user_profile_id)

        # make user a superuser
        self.userprofile.user.is_superuser = True
        self.userprofile.user.save()

        # remove this user from all the projects
        for p in Project.objects.all():
            p.team.remove(self.user_profile_id)
            p.team.add(user_profile_id)

            # this user doesn't belong to any project anymore
            self.assertFalse(p.team.filter(id=self.user_profile_id).exists())
            self.assertFalse(p.viewers.filter(id=self.user_profile_id).exists())

            # the project belongs to the new user now
            self.assertTrue(p.team.filter(id=user_profile_id).exists())

        # superuser still has access to the project
        url = reverse("project-retrieve", kwargs={"pk": p_in_country.id})
        response = self.test_user_client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        # access member only property
        self.assertIsInstance(response.json()['published']['start_date'], str)
        # access draft which is only for members only by default
        self.assertEqual(response.json()['draft']['name'], p_in_country.name)

        # superuser still has access to the project
        url = reverse("project-retrieve", kwargs={"pk": p_not_in_country.id})
        response = self.test_user_client.get(url, format="json")
        # access member only property
        self.assertIsInstance(response.json()['published']['start_date'], str)
        # access draft which is only for members only by default
        self.assertEqual(response.json()['draft']['name'], p_not_in_country.name)

        # Only works for retrieve, the list won't list any project that are not his/her
        url = reverse("project-list", kwargs={'list_name': 'member-of'})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    def test_map_project_country_view(self):
        url = reverse("project-map")
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['id'], self.project_id)
        self.assertEqual(response.json()[0]['name'], self.project_data['project']['name'])
        self.assertEqual(response.json()[0]['country'], self.country_id)

    def test_remove_stale_donors_from_projects(self):
        project = Project.objects.last()
        self.assertEqual(project.data['donors'], [self.d1.id, self.d2.id])

        Donor.objects.get(id=self.d2.id).delete()
        Project.remove_stale_donors()
        project.refresh_from_db()
        self.assertEqual(project.data['donors'], [self.d1.id])

    def test_unpublish_project(self):
        data = copy.deepcopy(self.project_data)
        data['project']['name'] = 'test unpublish'

        # create project draft
        url = reverse('project-create', kwargs={'country_office_id': self.country_office.id})
        response = self.test_user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        resp_data = response.json()
        self.assertEqual(resp_data['public_id'], '')

        project = Project.objects.get(id=resp_data['id'])
        self.assertEqual(project.data, {})

        self.check_project_search_init_state(project)

        # publish project
        url = reverse('project-publish', kwargs={'project_id': resp_data['id'],
                                                 'country_office_id': self.country_office.id})
        response = self.test_user_client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        resp_data = response.json()
        self.assertNotEqual(resp_data['public_id'], '')

        project.refresh_from_db()
        self.assertNotEqual(project.data, {})

        # check project search
        self.assertEqual(project.search.project_id, project.id)
        self.assertNotEqual(project.search.country_office_id, None)
        self.assertNotEqual(project.search.country_id, None)
        self.assertNotEqual(project.search.organisation_id, None)
        self.assertNotEqual(project.search.donors, [])
        self.assertNotEqual(project.search.software, [])
        self.assertNotEqual(project.search.hsc, [])
        self.assertNotEqual(project.search.hfa_categories, [])

        # unpublish project
        url = reverse('project-unpublish', kwargs={'project_id': resp_data['id']})
        response = self.test_user_client.put(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        resp_data = response.json()
        self.assertEqual(resp_data['public_id'], '')

        project.refresh_from_db()
        self.assertEqual(project.data, {})

        self.check_project_search_init_state(project)

    def test_project_publish_as_latest(self):
        data = copy.deepcopy(self.project_data)
        data['project']['name'] = 'test publish as latest'

        # create project draft
        url = reverse('project-create', kwargs={'country_office_id': self.country_office.id})
        response = self.test_user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        resp_data = response.json()
        self.assertEqual(resp_data['public_id'], '')

        project = Project.objects.get(id=resp_data['id'])
        self.assertEqual(project.data, {})

        # try to publish as latest (should fail)
        publish_as_latest_url = reverse('project-publish-as-latest', args=[project.id])
        response = self.test_user_client.get(publish_as_latest_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.json())

        # publish project
        url = reverse('project-publish', kwargs={'project_id': resp_data['id'],
                                                 'country_office_id': self.country_office.id})
        response = self.test_user_client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        resp_data = response.json()
        self.assertNotEqual(resp_data['public_id'], '')

        project.refresh_from_db()
        self.assertNotEqual(project.data, {})

        # try to publish as latest again
        response = self.test_user_client.get(publish_as_latest_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        resp_modified_datetime = datetime.strptime(response.json()['published']['modified'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.assertGreater(timezone.make_aware(resp_modified_datetime, pytz.UTC), project.modified)

    def test_add_new_users_by_invalid_email(self):
        url = reverse("project-groups", kwargs={"pk": self.project_id})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)

        groups = {
            "team": [],
            "viewers": [],
            "new_team_emails": ["new_email"],
            "new_viewer_emails": ["yolo"]
        }
        response = self.test_user_client.put(url, groups, format="json")

        self.assertEqual(
            response.json(), {'new_team_emails': {'0': ['Incorrect email address.', 'Enter a valid email address.']},
                              'new_viewer_emails': {'0': ['Incorrect email address.', 'Enter a valid email address.']}})

    def test_add_new_users_by_email(self):
        url = reverse("project-groups", kwargs={"pk": self.project_id})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserProfile.objects.count(), 1)
        owner_id = response.json()['team'][0]

        groups = {
            "team": [],
            "viewers": [],
            "new_team_emails": ["new_email@unicef.org"],
            "new_viewer_emails": ["new_email@pulilab.com"]
        }
        response = self.test_user_client.put(url, groups, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        self.assertTrue(response.json()['team'])
        self.assertTrue(response.json()['viewers'])
        self.assertTrue(owner_id not in response.json()['team'])
        self.assertEqual(UserProfile.objects.count(), 3)

    def test_add_new_users_by_already_existing_email(self):
        url = reverse("project-groups", kwargs={"pk": self.project_id})
        response = self.test_user_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserProfile.objects.count(), 1)
        owner_id = response.json()['team'][0]
        owner_email = UserProfile.objects.get().user.email

        groups = {
            "team": [owner_id],
            "viewers": [],
            "new_team_emails": [owner_email],
            "new_viewer_emails": [owner_email]
        }
        response = self.test_user_client.put(url, groups, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        self.assertTrue(owner_id in response.json()['team'])
        self.assertTrue(owner_id in response.json()['viewers'])
        self.assertEqual(UserProfile.objects.count(), 1)

    def test_publish_with_new_links(self):
        url = reverse("project-publish",
                      kwargs={"project_id": self.project_id, "country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        long_link = "https://longurl.com/fist-phase-is-short/second-phase-followed-by-a-short-prose/" \
                    "in-order-to-test-if-we-can-indeed-handle-long-links-which-should-be/" \
                    "way-over-200-characters-long/because-this-would-be-a-serious-limitation-were-it-not-the-case" \
                    "/but-we-can-handle-this-very-long-url-quite-easily/and-indeed-we-should-we-cannot-stress" \
                    "-the-outmost-importance-of-this-issue-at-hand"
        new_links = [dict(link_type=0, link_url=long_link),
                     dict(link_type=1, link_url="https://NEWsharepoint.directory")]
        data['project']['links'] = new_links
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['published']["links"], new_links)

    def test_publish_with_more_than_5_partners(self):
        url = reverse("project-publish",
                      kwargs={"project_id": self.project_id, "country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        new_partners = [dict(partner_type=0, partner_name="test partner 1", partner_email="p1@partner.ppp",
                             partner_contact="test partner contact 1", partner_website="https://partner1.com"),
                        dict(partner_type=1, partner_name="test partner 2", partner_email="p2@partner.ppp",
                             partner_contact="test partner contact 2", partner_website="https://partner2.com"),
                        dict(partner_type=2, partner_name="test partner 3", partner_email="p3@partner.ppp",
                             partner_contact="test partner contact 3", partner_website="https://partner3.com"),
                        dict(partner_type=3, partner_name="test partner 4", partner_email="p4@partner.ppp",
                             partner_contact="test partner contact 4", partner_website="https://partner4.com"),
                        dict(partner_type=1, partner_name="test partner 5", partner_email="p5@partner.ppp",
                             partner_contact="test partner contact 5", partner_website="https://partner5.com"),
                        dict(partner_type=0, partner_name="test partner 6", partner_email="p6@partner.ppp",
                             partner_contact="test partner contact 6", partner_website="https://partner6.com"),
                        ]
        data['project']['partners'] = new_partners
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['published']["partners"], new_partners)
        self.assertEqual(len(response.json()['published']["partners"]), 6)

    def test_favorite_projects(self):
        # create 5 projects
        project_ids = list()
        for _ in range(5):
            project_id = self.create_new_project()[0]
            project_ids.append(project_id)
        # create test user
        user_x_pr_id, user_x_client, user_x_key = self.create_user('train@choochoo.com', '12345789TIZ', '12345789TIZ')
        url_profile_details = reverse("userprofile-detail", kwargs={"pk": user_x_pr_id})
        response = user_x_client.get(url_profile_details)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['favorite']), 0)
        # get user's favorite list
        url_fav_list = reverse("project-list", kwargs={'list_name': 'favorite'})
        response = user_x_client.get(url_fav_list)
        self.assertEqual(response.json()['count'], 0)
        # add projects[0] to the user's favorite list
        url_add = reverse('projects-add-favorite', kwargs={'pk': project_ids[0]})
        response = user_x_client.put(url_add, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['favorite'], [project_ids[0]])
        # add projects[1] to the user's favorite list
        url_add = reverse('projects-add-favorite', kwargs={'pk': project_ids[1]})
        response = user_x_client.put(url_add, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['favorite'], [project_ids[0], project_ids[1]])
        # add projects[2] to the user's favorite list
        url_add = reverse('projects-add-favorite', kwargs={'pk': project_ids[2]})
        response = user_x_client.put(url_add, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['favorite'], project_ids[:3])
        # check favorite list
        response = user_x_client.get(url_fav_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
        self.assertEqual(set([p['id'] for p in response.json()['results']]),
                         {project_ids[0], project_ids[1], project_ids[2]})
        # unpublish projects[1]
        url = reverse('project-unpublish', kwargs={'project_id': project_ids[1]})
        response = self.test_user_client.put(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())
        resp_data = response.json()
        self.assertEqual(resp_data['public_id'], '')
        # expect the unpublished project to be removed from favorites
        response = user_x_client.get(url_profile_details)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['favorite'], [project_ids[0], project_ids[2]])
        response = user_x_client.get(url_fav_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(set([p['id'] for p in response.json()['results']]), {project_ids[0], project_ids[2]})
        # remove project from the user's favorite list
        url_remove = reverse('projects-remove-favorite', kwargs={'pk': project_ids[0]})
        response = user_x_client.put(url_remove, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['favorite'], [project_ids[2]])
        response = user_x_client.get(url_fav_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual([p['id'] for p in response.json()['results']], [project_ids[2]])

    @mock.patch('project.views.notify_superusers_about_new_pending_approval.apply_async')
    def test_technology_platform_create(self, notify_superusers_about_new_pending_approval):

        user = User.objects.create_user(username='test_user_100000', password='test_user_100000')
        user_profile = UserProfile.objects.create(user=user, name="test_user_100000")

        data = {
            'name': 'test platform',
            'state': TechnologyPlatform.APPROVED,  # should have no effect
            'added_by': user_profile.id,  # should have no effect
        }
        url = reverse('technologyplatform-list')
        response = self.test_user_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        data = response.json()
        self.assertEqual(data['state'], TechnologyPlatform.PENDING)
        self.assertEqual(data['added_by'], self.user_profile_id)

        software = TechnologyPlatform.objects.get(id=data['id'])

        notify_superusers_about_new_pending_approval.assert_called_once_with((software._meta.model_name, software.pk))

    @mock.patch('project.tasks.send_mail_wrapper')
    def test_notify_super_users_about_pending_software_success(self, send_email):
        super_users = User.objects.filter(is_superuser=True)
        # remove super user status from the current super users
        for user in super_users:
            user.is_superuser = False
            user.save()

        test_super_user_1 = User.objects.create_superuser(username='superuser_1', email='s1@pulilab.com', 
                                                          password='puli_1234', is_staff=True, is_superuser=True)
        test_super_user_2 = User.objects.create_superuser(username='superuser_2', email='s2@pulilab.com', 
                                                          password='puli_1234', is_staff=True, is_superuser=True)
        try:
            software = TechnologyPlatform.objects.create(name='pending software', state=TechnologyPlatform.PENDING)
            notify_superusers_about_new_pending_approval.apply((software._meta.model_name, software.id))

            call_args_list = send_email.call_args_list[0][1]
            self.assertEqual(call_args_list['subject'], f'New {software._meta.model_name} is pending for approval')
            self.assertEqual(call_args_list['email_type'], 'new_pending_approval')
            self.assertIn(test_super_user_1.email, call_args_list['to'])
            self.assertIn(test_super_user_2.email, call_args_list['to'])
            self.assertEqual(call_args_list['context']['object_name'], software.name)

        finally:
            test_super_user_1.delete()
            test_super_user_2.delete()

            # give back super user status
            for user in super_users:
                user.is_superuser = True
                user.save()

    @mock.patch('project.tasks.send_mail_wrapper', return_value=None)
    def test_notify_user_about_software_approve(self, send_email):
        software = TechnologyPlatform.objects.create(name='pending software', state=TechnologyPlatform.PENDING, 
                                                     added_by_id=self.user_profile_id)
        notify_user_about_approval.apply(args=('test', software._meta.model_name, software.id))
        notify_user_about_approval.apply(args=('approve', software._meta.model_name, software.id))

        send_email.assert_called_once()
        call_args_list = send_email.call_args_list[0][1]
        self.assertEqual(call_args_list['subject'], f"`{software.name}` you requested has been approved")
        self.assertEqual(call_args_list['email_type'], 'object_approved')
        self.assertEqual(call_args_list['context']['object_name'], software.name)

    @mock.patch('project.tasks.send_mail_wrapper', return_value=None)
    def test_notify_user_about_software_decline(self, send_email):
        software = TechnologyPlatform.objects.create(name='pending software', state=TechnologyPlatform.PENDING, 
                                                     added_by_id=self.user_profile_id)
        notify_user_about_approval.apply(args=('decline', software._meta.model_name, software.id))

        call_args_list = send_email.call_args_list[0][1]
        self.assertEqual(call_args_list['subject'], f"`{software.name}` you requested has been declined")
        self.assertEqual(call_args_list['email_type'], 'object_declined')
        self.assertEqual(call_args_list['context']['object_name'], software.name)

    @mock.patch('project.tasks.send_mail_wrapper', return_value=None)
    def test_notify_user_about_software_approval_fail(self, send_email):
        software = TechnologyPlatform.objects.create(name='pending software')
        notify_user_about_approval.apply(args=('approve', software._meta.model_name, software.id))

        send_email.assert_not_called()

    @mock.patch('project.tasks.notify_user_about_approval.apply_async', return_value=None)
    def test_software_decline(self, notify_user_about_approval):
        software_1 = TechnologyPlatform.objects.create(name='approved software')
        software_2 = TechnologyPlatform.objects.create(name='will be declined', state=TechnologyPlatform.PENDING)

        data, org, country, country_office, d1, d2 = self.create_test_data(name="Test Project 10000")
        data['project']['platforms'] = [software_1.id, software_2.id]

        url = reverse("project-create", kwargs={"country_office_id": country_office.id})
        response = self.test_user_client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())

        project = Project.objects.get(pk=response.json()['id'])
        self.assertEqual(len(project.draft['platforms']), 2)

        url = reverse("project-publish", kwargs={"project_id": project.id,
                                                 "country_office_id": country_office.id})
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.json())

        project.refresh_from_db()
        self.assertEqual(len(project.draft['platforms']), 2)
        self.assertEqual(len(project.data['platforms']), 2)

        # decline software
        software_2.state = TechnologyPlatform.DECLINED
        software_2.save()

        project.refresh_from_db()
        self.assertEqual(len(project.draft['platforms']), 1)
        self.assertEqual(project.draft['platforms'][0], software_1.id)
        self.assertEqual(len(project.data['platforms']), 1)
        self.assertEqual(project.data['platforms'][0], software_1.id)

        notify_user_about_approval.assert_called_once_with(args=('decline', 
                                                                 software_2._meta.model_name, software_2.pk))

    @override_settings(MIGRATE_PHASES=True)
    @mock.patch('project.utils.ID_MAP', {"3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6})
    def test_phases_are_migrated_to_stages(self):
        ID_MAP = {"3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6}

        url = reverse("project-create", kwargs={"country_office_id": self.country_office.id})
        data = copy.deepcopy(self.project_data)
        non_migratable_phase = 1
        data['project'].update(dict(
            name="Test Project4",
            phase=non_migratable_phase
        ))
        data['project'].pop('stages', None)
        self.assertFalse(str(non_migratable_phase) in ID_MAP)
        response = self.test_user_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)

        # we have deleted the ignorable phase
        self.assertTrue('stages' not in response.json()['draft'])
        self.assertTrue('phase' not in response.json()['draft'])
        self.assertFalse(response.json()['published'])

        migratable_phase = random.choice(list(ID_MAP.keys()))
        data['project'].update(dict(
            name="Test Project5",
            phase=int(migratable_phase)
        ))
        response = self.test_user_client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)

        # we have migrated the migratable phase
        self.assertTrue('stages' in response.json()['draft'])
        self.assertTrue('phase' not in response.json()['draft'])
        self.assertFalse(response.json()['published'])
        self.assertEqual(response.json()['draft']['stages'], [dict(id=ID_MAP[migratable_phase])])

    def test_project_landing_blocks(self):
        project_id2, project_data, org, c, uoffice, d1, d2 = self.create_new_project(name="Test Project 2")
        project_id3, project_data, org, c, uoffice, d1, d2 = self.create_new_project(name="Test Project 3")
        project_id4, project_data, org, c, uoffice, d1, d2 = self.create_new_project(name="Test Project 4")
        project_id5, project_data, org, c, uoffice, d1, d2 = self.create_new_project(name="Test Project 5 not mine")

        p1 = Project.objects.get(id=self.project_id)
        p2 = Project.objects.get(id=project_id2)
        p3 = Project.objects.get(id=project_id3)
        p4 = Project.objects.get(id=project_id4)
        p1.featured = True
        p1.featured_rank = 1
        p1.save()
        p2.featured = True
        p2.featured_rank = 2
        p2.save()
        p3.featured = True
        p3.featured_rank = 3
        p3.save()
        p4.featured = True
        p4.featured_rank = 4
        p4.save()

        user2_profile_id, test_user_client, test_user_key = self.create_user('user2@unicef.org', 'A@r!1234', 'A@r!1234')
        p5 = Project.objects.get(id=project_id5)
        p5.team.set([user2_profile_id])
        p4.team.set([self.user_profile_id, user2_profile_id])

        url = reverse("project-landing")
        response = self.test_user_client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['my_initiatives_count'], 4)
        self.assertEqual(len(data['my_initiatives']), 3)
        self.assertEqual(len(data['recents']), 1)
        self.assertEqual(len(data['featured']), 4)

        response = test_user_client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_project_add_image(self):
        url = reverse("projects-add-image", kwargs={"pk": self.project_id})
        image = get_temp_image("image")
        data = {
            "image": image
        }
        response = self.test_user_client.put(url, data=data, format='multipart', HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('source_images/image.png' in response.json()['image'])
        self.assertTrue(response.json()['thumbnail'])

    def test_country_manager_projects(self):
        # create 5 projects
        project_co_dict = dict()
        for _ in range(5):
            project_id, project_data, org, country, country_office, d1, d2 = self.create_new_project()
            project_co_dict[project_id] = country_office.id

        url = reverse("project-list", kwargs={'list_name': 'country-manager'})
        response = self.test_user_client.get(url)
        self.assertEqual(response.json()['count'], 0)

        # add our user as a country manager of the country offices
        self.userprofile.manager_of.set(list(set(project_co_dict.values())))

        url = reverse("project-list", kwargs={'list_name': 'country-manager'})
        response = self.test_user_client.get(url)
        self.assertEqual(response.json()['count'], 5)

    def test_country_manager_export(self):
        response = self.test_user_client.get(reverse("country-manager-export"))
        self.assertTrue(response.content)
        self.assertTrue('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        in response._content_type_for_repr)

    def test_project_end_date_wrong_format(self):
        data = copy.deepcopy(self.project_data)
        data['project']['end_date'] = "1970aaa"

        url = reverse("project-publish", kwargs={"project_id": self.project_id,
                                                 "country_office_id": self.country_office.id})
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'project': {'end_date': ['Wrong date format']}})

    def test_project_start_date_wrong_format(self):
        data = copy.deepcopy(self.project_data)
        data['project']['start_date'] = "1970aaa"

        url = reverse("project-publish", kwargs={"project_id": self.project_id,
                                                 "country_office_id": self.country_office.id})
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'project': {'start_date': ['Wrong date format']}})

    def test_project_end_date_earlier_than_start_date(self):
        data = copy.deepcopy(self.project_data)
        data['project']['start_date'] = str(datetime.today().date())
        data['project']['end_date'] = str(datetime.today().date() - timedelta(days=1))

        url = reverse("project-publish", kwargs={"project_id": self.project_id,
                                                 "country_office_id": self.country_office.id})
        response = self.test_user_client.put(url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'project': {'end_date': ['End date cannot be earlier than start date']}})
