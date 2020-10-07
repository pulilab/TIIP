from django.urls import reverse

from project.models import ProblemStatement, ProjectPortfolioState, Project
from project.tests.portfolio_tests import PortfolioSetup


class PortfolioSearchTests(PortfolioSetup):
    def setUp(self):
        super().setUp()

        self.project2_id, *_ = self.create_new_project(self.user_2_client)
        self.project3_id, *_ = self.create_new_project(self.user_2_client)
        self.project4_id, *_ = self.create_new_project(self.user_2_client)
        self.project5_id, *_ = self.create_new_project(self.user_2_client)

        response = self.create_portfolio("Test Portfolio 2", "Port-o-folio", [self.user_3_pr_id], self.user_2_client)
        self.assertEqual(response.status_code, 201, response.json())
        self.portfolio2_id = response.json()['id']
        
        self.scores = {
            'psa': [ProblemStatement.objects.get(name="PS 1", portfolio_id=self.portfolio_id).id],
            'rnci': 2,
            'ratp': 4,
            'ra': 5,
            'ee': 5,
            'nst': 5,
            'nc': 5,
            'ps': 5,
            'impact': 5,
            'scale_phase': 6
        }

        # add Project 2, 4 to a Portfolio
        url = reverse("portfolio-project-add", kwargs={"pk": self.portfolio_id})
        request_data = {"project": [self.project2_id, self.project4_id]}
        response = self.user_2_client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 201, response.json())

        # review and approve Project 2, 4
        pps2 = ProjectPortfolioState.objects.get(project_id=self.project2_id, portfolio_id=self.portfolio_id)
        pps4 = ProjectPortfolioState.objects.get(project_id=self.project4_id, portfolio_id=self.portfolio_id)
        self.review_and_approve_project(pps2, self.scores, self.user_2_client)
        self.review_and_approve_project(pps4, self.scores, self.user_2_client)

    def test_list_all_in_portfolio_for_detail_page(self):
        url = reverse("search-project-list")
        data = {"portfolio": self.portfolio_id, "type": "portfolio"}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(response.json()['results']['projects'][0]['id'], self.project2_id)
        self.assertEqual(response.json()['results']['projects'][0]['portfolio'], self.portfolio_id)
        self.assertEqual(response.json()['results']['projects'][1]['id'], self.project4_id)
        self.assertEqual(response.json()['results']['projects'][1]['portfolio'], self.portfolio_id)

    def test_multi_portfolio_filter_should_not_work(self):
        # add Project 3 to a Portfolio 2
        self.move_project_to_portfolio(self.portfolio2_id, self.project3_id, 201, self.user_2_client)
        pps3 = ProjectPortfolioState.objects.get(project_id=self.project3_id, portfolio_id=self.portfolio2_id)
        self.review_and_approve_project(pps3, self.scores, self.user_2_client)
        
        # it only finds the last query param
        url = reverse("search-project-list")
        data = {"portfolio": [self.portfolio_id, self.portfolio2_id], "type": "portfolio"}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results']['projects'][0]['id'], self.project3_id)
        self.assertEqual(response.json()['results']['projects'][0]['portfolio'], self.portfolio2_id)

    def test_search_within_a_portfolio(self):
        new_project_id, *_ = self.create_new_project(self.user_2_client, name="New Project 1")

        # add new project to a Portfolio 1 and review + approve
        self.move_project_to_portfolio(self.portfolio_id, new_project_id, 201, self.user_2_client)
        pps = ProjectPortfolioState.objects.get(project_id=new_project_id, portfolio_id=self.portfolio_id)
        self.review_and_approve_project(pps, self.scores, self.user_2_client)

        url = reverse("search-project-list")
        data = {"q": "New", "in": "name", "portfolio": self.portfolio_id, "type": "portfolio"}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

        url = reverse("search-project-list")
        data = {"q": "project", "in": "name", "portfolio": self.portfolio_id, "type": "portfolio"}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)

    def test_filter_and_search_within_a_portfolio(self):
        new_project_id, project_data, org, country, *_ = self.create_new_project(
            self.user_2_client, name="New Project 1")

        # add new project to a Portfolio 1 and review + approve
        self.move_project_to_portfolio(self.portfolio_id, new_project_id, 201, self.user_2_client)
        pps = ProjectPortfolioState.objects.get(project_id=new_project_id, portfolio_id=self.portfolio_id)
        self.review_and_approve_project(pps, self.scores, self.user_2_client)

        url = reverse("search-project-list")
        data = {"q": "New", "in": "name", "country": country.id, "portfolio": self.portfolio_id, "type": "portfolio"}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_scale_phase_filter_on_portfolio(self):
        new_project_id, project_data, org, country, *_ = self.create_new_project(
            self.user_2_client, name="New Project 1")

        # add new project to a Portfolio 1
        self.move_project_to_portfolio(self.portfolio_id, new_project_id, 201, self.user_2_client)

        review_data_complete = {
            'psa': [ProblemStatement.objects.get(name="PS 1", portfolio_id=self.portfolio_id).id],
            'rnci': 2,
            'ratp': 4,
            'ra': 5,
            'ee': 5,
            'nst': 5,
            'nc': 5,
            'ps': 5,
            'impact': 5,
            'scale_phase': 2
        }
        
        pps = ProjectPortfolioState.objects.get(project_id=new_project_id, portfolio_id=self.portfolio_id)
        url = reverse('portfolio-project-manager-review', kwargs={'pk': pps.id})
        response = self.user_2_client.post(url, review_data_complete, format="json")
        self.assertEqual(response.status_code, 200)
        pps.refresh_from_db()
        self.assertEqual(pps.reviewed, True)
        self.assertEqual(pps.approved, False)

        url = reverse("search-project-list")
        data = {"portfolio": self.portfolio_id, "type": "portfolio", "sp": ProjectPortfolioState.SCALE_CHOICES[1][0]}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

        # now reviewed, approve project
        url = reverse('portfolio-project-approve', kwargs={'pk': self.portfolio_id})
        project_data = {'project': [new_project_id]}
        response = self.user_2_client.post(url, project_data, format="json")
        self.assertEqual(response.status_code, 200)
        pps.refresh_from_db()
        self.assertEqual(pps.approved, True)
        
        url = reverse("search-project-list")
        data = {"portfolio": self.portfolio_id, "type": "portfolio", "sp": ProjectPortfolioState.SCALE_CHOICES[0][0]}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

        url = reverse("search-project-list")
        data = {"portfolio": self.portfolio_id, "type": "portfolio", "sp": ProjectPortfolioState.SCALE_CHOICES[1][0]}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results']['projects'][0]['scale_phase'], 
                         ProjectPortfolioState.SCALE_CHOICES[1][0])

    def test_problem_statement_filter_on_portfolio(self):
        new_project_id, project_data, org, country, *_ = self.create_new_project(
            self.user_2_client, name="New Project 1")

        # add new project to a Portfolio 1
        self.move_project_to_portfolio(self.portfolio_id, new_project_id, 201, self.user_2_client)

        ps1 = ProblemStatement.objects.get(name="PS 1", portfolio_id=self.portfolio_id)
        ps2 = ProblemStatement.objects.get(name="PS 2", portfolio_id=self.portfolio_id)
        review_data_complete = {
            'psa': [ps1.id, ps2.id],
            'rnci': 2,
            'ratp': 4,
            'ra': 5,
            'ee': 5,
            'nst': 5,
            'nc': 5,
            'ps': 5,
            'impact': 5,
            'scale_phase': 6
        }

        pps1 = ProjectPortfolioState.objects.get(project_id=new_project_id, portfolio_id=self.portfolio_id)
        url = reverse('portfolio-project-manager-review', kwargs={'pk': pps1.id})
        response = self.user_2_client.post(url, review_data_complete, format="json")
        self.assertEqual(response.status_code, 200)
        pps1.refresh_from_db()
        self.assertEqual(pps1.reviewed, True)
        self.assertEqual(pps1.approved, False)

        pps2 = ProjectPortfolioState.objects.get(project_id=self.project2_id, portfolio_id=self.portfolio_id)
        self.assertEqual(pps2.reviewed, True)
        self.assertEqual(pps2.approved, True)
        pps4 = ProjectPortfolioState.objects.get(project_id=self.project4_id, portfolio_id=self.portfolio_id)
        self.assertEqual(pps4.reviewed, True)
        self.assertEqual(pps4.approved, True)

        url = reverse("search-project-list")
        data = {"portfolio": self.portfolio_id, "type": "portfolio", "ps": ps1.id}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)

        # now reviewed, approve project
        url = reverse('portfolio-project-approve', kwargs={'pk': self.portfolio_id})
        project_data = {'project': [new_project_id]}
        response = self.user_2_client.post(url, project_data, format="json")
        self.assertEqual(response.status_code, 200)
        pps1.refresh_from_db()
        self.assertEqual(pps1.approved, True)

        url = reverse("search-project-list")
        data = {"portfolio": self.portfolio_id, "type": "portfolio", "ps": 999}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

        url = reverse("search-project-list")
        data = {"portfolio": self.portfolio_id, "type": "portfolio", "ps": ps1.id}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
        
        url = reverse("search-project-list")
        data = {"portfolio": self.portfolio_id, "type": "portfolio", "ps": ps2.id}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_portfolio_inventory_for_managers(self):
        self.assertEqual(Project.objects.count(), 5)
        
        url = reverse("search-project-list")
        data = {"portfolio": self.portfolio_id, "type": "portfolio", "ps": 99, "sp": 99, "portfolio_page": "inventory"}
        response = self.user_2_client.get(url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)

        pass
