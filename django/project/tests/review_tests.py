from project.models import Portfolio, Project, ProjectPortfolioState, ReviewScore, ProblemStatement
from user.models import UserProfile
from project.tests.portfolio_tests import PortfolioSetup
from django.urls import reverse
from random import randint


class ReviewTests(PortfolioSetup):
    def setUp(self):
        super(ReviewTests, self).setUp()
        # User roles: User 1 (normal user), User 2 (global portfolio owner), User 3 (manager of portfolio 1)
        self.project = Project.objects.get(id=self.project_1_id)
        self.portfolio = Portfolio.objects.get(id=self.portfolio_id)
        # add other project
        self.project_rev_id, project_data, org, country, country_office, d1, d2 = \
            self.create_new_project(self.user_1_client)

        # Add project to portfolio
        # check permissions with user_1_client, which is not allowed
        self.move_project_to_portfolio(self.portfolio_id, self.project_rev_id, 403, self.user_1_client)
        # do it with user 3, who is a GPO
        response_json = self.move_project_to_portfolio(self.portfolio_id, self.project_rev_id, 201, self.user_3_client)
        pps_data = response_json['review_states']
        self.assertEqual(len(pps_data), 1)
        self.assertEqual(pps_data[0]['project'], self.project_rev_id)

        self.project_rev = Project.objects.get(id=self.project_rev_id)
        self.pps = ProjectPortfolioState.objects.get(portfolio=self.portfolio, project=self.project_rev)
        self.user_1_profile = UserProfile.objects.get(id=self.user_1_pr_id)

    def test_project_in_portfolio_status_changes(self):
        project_id, project_data, org, country, country_office, d1, d2 = \
            self.create_new_project(self.user_1_client)

        portfolio = Portfolio.objects.get(id=self.portfolio_id)
        pps_data = portfolio.review_states.all()
        self.assertEqual(len(pps_data), 1)
        self.assertEqual(pps_data[0].project.id, self.project_rev_id)
        # Moving project from inventory to review state
        # Try the API with incorrect data
        url = reverse('portfolio-project-add', kwargs={'pk': self.portfolio_id})
        response = self.user_3_client.post(url, {}, format="json")
        self.assertEqual(response.status_code, 400)
        response = self.user_3_client.post(url, {'project': []}, format="json")
        self.assertEqual(response.status_code, 400)
        response = self.user_3_client.post(url, {'project': [25000]}, format="json")
        self.assertEqual(response.status_code, 400)
        # do it the right way
        pps_data = self.move_project_to_portfolio(self.portfolio_id, project_id, 201)['review_states']
        self.assertEqual(len(pps_data), 2)
        # Moving project from review to approved state
        # Try to approve project without official manager review
        url = reverse('portfolio-project-approve', kwargs={'pk': self.portfolio_id})
        project_data = {'project': [self.project_rev_id]}
        response = self.user_3_client.post(url, project_data, format="json")
        self.assertEqual(response.status_code, 400)
        # Try to review portfolio as user 1 (not a GPO or manager)
        url = reverse('portfolio-project-manager-review', kwargs={'pk': self.pps.id})
        response = self.user_1_client.post(url, {}, format="json")
        self.assertEqual(response.status_code, 403)
        # try to review portfolio as user 3 portfolio manager
        review_data_incomplete = {
            # missing scale phase and impact
            'psa': [ProblemStatement.objects.get(name="PS 1").id],
            'rnci': 2,
            'ratp': 4,
            'ra': 5,
            'ee': 5,
            'nst': 5,
            'nc': 5,
            'ps': 5
        }
        response = self.user_3_client.post(url, review_data_incomplete, format="json")
        self.assertEqual(response.status_code, 400)
        expected_errors = {'impact': ['This field is required.'], 'scale_phase': ['This field is required.']}
        self.assertEqual(response.json(), expected_errors)
        review_data_complete = {
            'psa': [ProblemStatement.objects.get(name="PS 1").id],
            'rnci': 2,
            'ratp': 4,
            'ra': 5,
            'ee': 5,
            'nst': 5,
            'nc': 5,
            'ps': 5,
            'impact': 6,
            'scale_phase': 5
        }
        response = self.user_3_client.post(url, review_data_complete, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'impact': ['"6" is not a valid choice.']})

        review_data_complete = {
            'psa': [ProblemStatement.objects.get(name="PS 1").id],
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
        response = self.user_3_client.post(url, review_data_complete, format="json")
        self.assertEqual(response.status_code, 200)
        self.pps.refresh_from_db()
        self.assertEqual(self.pps.reviewed, True)
        self.assertEqual(self.pps.approved, False)

        # Edit the official review of the project
        review_data_complete['nc'] = 4
        response = self.user_3_client.post(url, review_data_complete, format="json")
        self.assertEqual(response.status_code, 200)
        self.pps.refresh_from_db()
        self.assertEqual(self.pps.nc, 4)
        self.assertEqual(self.pps.reviewed, True)
        self.assertEqual(self.pps.approved, False)

        # now reviewed, approve project
        url = reverse('portfolio-project-approve', kwargs={'pk': self.portfolio_id})
        project_data = {'project': [self.project_rev_id]}
        response = self.user_3_client.post(url, project_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.pps.refresh_from_db()
        self.assertEqual(self.pps.approved, True)
        # try to modify the approved project
        url = reverse('portfolio-project-manager-review', kwargs={'pk': self.pps.id})
        review_data_complete['nc'] = 3
        response = self.user_3_client.post(url, review_data_complete, format="json")
        self.assertEqual(response.status_code, 403)
        self.pps.refresh_from_db()
        self.assertEqual(self.pps.nc, 4)
        self.assertEqual(self.pps.reviewed, True)
        self.assertEqual(self.pps.approved, True)
        # Moving project from approved to review state
        url = reverse('portfolio-project-disapprove', kwargs={'pk': self.portfolio_id})
        project_data = {'project': [self.project_rev_id]}
        response = self.user_3_client.post(url, project_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.pps.refresh_from_db()
        self.assertEqual(self.pps.approved, False)

        # Moving project from review state to inventory
        # Try the API with incorrect data
        pps_ids = {x['id'] for x in pps_data}
        pps_projects = {x['project'] for x in pps_data}
        self.assertEqual(pps_projects, {self.project_rev_id, project_id})
        url = reverse('portfolio-project-remove', kwargs={'pk': self.portfolio_id})
        response = self.user_3_client.post(url, {}, format="json")
        self.assertEqual(response.status_code, 400)
        response = self.user_3_client.post(url, {'project': []}, format="json")
        self.assertEqual(response.status_code, 400)
        response = self.user_3_client.post(url, {'project': [25000]}, format="json")
        self.assertEqual(response.status_code, 400)
        response = self.user_3_client.post(url, {'project': [project_id]}, format="json")
        self.assertEqual(response.status_code, 200, response.json())
        pps = ProjectPortfolioState.all_objects.get(project_id=project_id)
        self.assertEqual(pps.is_active, False)
        pps_data = response.json()['review_states']
        self.assertEqual(len(pps_data), 1)
        self.assertEqual(pps_data[0]['project'], self.project_rev_id)
        # Re-add the project review to the portfolio
        url = reverse('portfolio-project-add', kwargs={'pk': self.portfolio_id})
        response = self.user_3_client.post(url, {'project': [project_id]}, format="json")
        self.assertEqual(response.status_code, 201)
        pps_ids_2 = {x['id'] for x in response.json()['review_states']}
        self.assertEqual(pps_ids_2, pps_ids)

    def test_review_assign_questions(self):
        url = reverse("portfolio-assign-questionnaire",
                      kwargs={"portfolio_id": self.portfolio_id, 'project_id': self.project_rev.id})
        request_data = {'userprofile': [self.user_1_profile.id]}
        response = self.user_3_client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        created = response.json()[0]['created']
        modified = response.json()[0]['modified']
        question_id = response.json()[0]['id']
        # Try to do it again
        response = self.user_3_client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        # check that the same, unchanged object is returned
        self.assertEqual(response.json()[0]['id'], question_id)
        self.assertEqual(response.json()[0]['created'], created)
        self.assertEqual(response.json()[0]['modified'], modified)
        url = reverse('review-score-get-or-delete', kwargs={'pk': question_id})
        response = self.user_3_client.delete(url, format="json")
        self.assertEqual(response.status_code, 204)
        # check if it was removed
        qs = ReviewScore.all_objects.filter(id=question_id)
        self.assertEqual(qs.count(), 0)

    def test_review_fill_scores(self):
        # create questions
        url = reverse("portfolio-assign-questionnaire",
                      kwargs={"portfolio_id": self.portfolio_id, 'project_id': self.project_rev_id})
        request_data = {'userprofile': [self.user_1_profile.id]}
        response = self.user_3_client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 200)

        question_id = response.json()[0]['id']
        pps_id = response.json()[0]['portfolio_review']
        # create a new user who is not associated with the review or the portfolio in any way
        user_x_pr_id, user_x_client, user_x_key = self.create_user('donkey@kong.com', '12345789TIZ', '12345789TIZ')
        partial_data = {
            'ee': 1,
            'ra': 5,
            'nc': 4,
            'nst_comment': 'I do not know how to set this'
        }
        url = reverse('review-score-fill', kwargs={"pk": question_id})
        # Try to fill the answers with the unauthorized user
        response = user_x_client.post(url, partial_data, format="json")
        self.assertEqual(response.status_code, 403)  # UNAUTHORIZED
        # try to fill in faulty data - should not be allowed
        faulty_data = {
            'nst': 7  # Not allowed value
        }
        url = reverse('review-score-fill', kwargs={"pk": question_id})
        response = self.user_1_client.post(url, faulty_data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['nst'], ['"7" is not a valid choice.'])

        response = self.user_1_client.post(url, partial_data, format="json")
        self.assertEqual(response.status_code, 200)

        # read pps data
        url = reverse('portfolio-project-manager-review', kwargs={'pk': pps_id})
        response = self.user_1_client.get(url, {}, format="json")
        self.assertEqual(response.status_code, 200)
        # no answer was finalized, averages should be empty!
        empty_averages = \
            {
                'ee': None,
                'nc': None,
                'nst': None,
                'ps': None,
                'ra': None,
                'ratp': None,
                'rnci': None
            }
        self.assertEqual(response.json()['averages'], empty_averages)

        # Finalize reviewscore
        url = reverse('review-score-fill', kwargs={"pk": question_id})
        response = self.user_1_client.post(url, {"status": ReviewScore.STATUS_COMPLETE}, format="json")
        self.assertEqual(response.status_code, 200)

        # add another user review
        user_y_pr_id, user_y_client, user_y_key = self.create_user('jeff@bezos.com', '12345789TIZ', '12345789TIZ')
        url = reverse("portfolio-assign-questionnaire",
                      kwargs={"portfolio_id": self.portfolio_id, 'project_id': self.project_rev_id})
        request_data = {'userprofile': [user_y_pr_id]}
        response = self.user_3_client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        question_id_y = response.json()[0]['id']
        # Score has not been edited yet, so status should be "pending"
        self.assertEqual(response.json()[0]['status'], ReviewScore.STATUS_PENDING)

        partial_data_2 = {
            'ee': 2,
            'ra': 4,
            'nst': 1,
            'nc': 2,
            'nst_comment': 'Neither do I'
        }
        url = reverse('review-score-fill', kwargs={"pk": question_id_y})
        response = user_y_client.post(url, partial_data_2, format="json")
        self.assertEqual(response.status_code, 200)
        # Score is not complete, so it needs to be in DRAFT status (even though we didn't send draft here
        self.assertEqual(response.json()['status'], ReviewScore.STATUS_DRAFT)

        # Finalize reviewscore
        url = reverse('review-score-fill', kwargs={"pk": question_id_y})
        response = user_y_client.post(url, {"status": ReviewScore.STATUS_COMPLETE}, format="json")
        self.assertEqual(response.status_code, 200)
        # Score is not complete, so it needs to be in DRAFT status (even though we didn't send draft here
        self.assertEqual(response.json()['status'], ReviewScore.STATUS_COMPLETE)

        # read pps data
        url = reverse('portfolio-project-manager-review', kwargs={'pk': pps_id})
        response = self.user_1_client.get(url, {}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['averages']['ee'], 1.5)
        self.assertEqual(response.json()['averages']['ra'], 4.5)
        self.assertEqual(response.json()['averages']['nst'], 1.0)
        self.assertEqual(response.json()['averages']['rnci'], None)
        self.assertEqual(response.json()['averages']['nc'], 3)
        self.assertEqual(len(response.json()['review_scores']), 2)

        # Try to modify the answers - should not be allowed
        partial_data = {
            'rnci_comment': "I always forget this!",
        }
        response = self.user_1_client.post(url, partial_data, format="json")
        self.assertEqual(response.status_code, 403)  # UNAUTHORIZED
        url = reverse('review-score-get-or-delete', kwargs={"pk": question_id})
        response = self.user_1_client.get(url, format="json")
        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data['ee'], 1)
        self.assertEqual(resp_data['ra'], 5)
        self.assertEqual(resp_data['rnci_comment'], None)
        url_rev_list = reverse("project-list", kwargs={'list_name': 'review'})
        response = self.user_1_client.get(url_rev_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)  # do not show completed reviews in this view

    def test_portfolio_matrix_output(self):
        """
        - Create 5 projects for the portfolio
        - Move 4 of them to review w. different scores and problem statements,
        - Query the detailed results
        - Check if the matrix blobs are correct
        """
        # create new portfolio
        response = self.create_portfolio('Matrix test portfolio', "Portfolio for testing matrix output",
                                         [self.user_3_pr_id], self.user_2_client)
        self.assertEqual(response.status_code, 201, response.json())
        portfolio_id = response.json()['id']
        project_ids = list()
        for _ in range(5):
            project_id = self.create_new_project(self.user_2_client)[0]
            project_ids.append(project_id)
            self.move_project_to_portfolio(portfolio_id, project_id)
        pps_list = Portfolio.objects.get(id=portfolio_id).review_states.all()
        problem_statements = list()
        for i in range(5):
            problem_statements.append(ProblemStatement.objects.create(
                name=f"PS_Portfolio_{i}", description=f"PS_{i} description",
                portfolio=Portfolio.objects.get(id=portfolio_id)))

        i = 0
        for pps in pps_list:
            psa_current = [problem_statements[j].pk for j in range(0, 5, i % 2 + 1)]

            scores = {
                'psa': psa_current,
                'rnci': randint(1, 5),
                'ratp': randint(1, 5),
                'ra': i % 2 + 1,
                'ee': randint(1, 5),
                'nst': i % 2 + 1,
                'nc': i % 2 + 1,
                'ps': randint(1, 5),
                'impact': i % 2 + 1,
                'scale_phase': randint(1, 5),
                'status': ReviewScore.STATUS_COMPLETE,
            }
            self.review_and_approve_project(pps, scores, self.user_2_client)
            i += 1

        portfolio = Portfolio.objects.get(id=portfolio_id)
        impact_data = portfolio.get_risk_impact_matrix()
        ambition_data = portfolio.get_ambition_matrix()
        self.assertEqual(len(impact_data), 2)
        self.assertEqual(len(ambition_data), 2)
        impact_ratios = {x['ratio'] for x in impact_data}
        ambition_ratios = {x['ratio'] for x in ambition_data}
        self.assertEqual(impact_ratios, {0.67, 1.0})
        self.assertEqual(ambition_ratios, {0.67, 1.0})
        problem_statement_matrix = portfolio.get_problem_statement_matrix()

        self.assertEqual(len(problem_statement_matrix['high_activity']), 0)
        self.assertEqual(len(problem_statement_matrix['moderate']), 5)
        self.assertEqual(len(problem_statement_matrix['neglected']), 2)

    def test_score_update(self):
        # create new portfolio
        problem_statements = [
            {
                "name": "PS 1",
                "description": "PS 1 description"
            },
            {
                "name": "PS 2",
                "description": "PS 2 description"
            },
            {
                "name": "PS 3",
                "description": "PS 3 description"
            }

        ]
        response = self.create_portfolio('Scores test portfolio', "Portfolio for testing scores output",
                                         [self.user_3_pr_id], self.user_2_client, problem_statements)
        self.assertEqual(response.status_code, 201, response.json())
        portfolio_id = response.json()['id']
        # create new project
        project_id = self.create_new_project(self.user_2_client)[0]
        # move it to the portfolio
        resp = self.move_project_to_portfolio(portfolio_id, project_id)
        portfolio_review_id = resp['review_states'][0]['id']
        portfolio_db = Portfolio.objects.get(id=portfolio_id)
        problem_statements = portfolio_db.problem_statements.all()

        # create user review
        user_y_pr_id, user_y_client, user_y_key = self.create_user('jeff@bezos.com', '12345789TIZ', '12345789TIZ')
        url = reverse("portfolio-assign-questionnaire",
                      kwargs={"portfolio_id": portfolio_id, 'project_id': project_id})
        request_data = {'userprofile': [user_y_pr_id]}
        response = self.user_3_client.post(url, request_data, format="json")
        self.assertEqual(response.status_code, 200)
        question_id_y = response.json()[0]['id']
        # do a partial update of the review by the user
        url = reverse('review-score-fill', kwargs={"pk": question_id_y})
        partial_data = {
            'overall_reviewer_feedback': "I'll finish this later, BRB"
        }
        response = user_y_client.patch(url, partial_data, format="json")
        expected_patch_response_1 = {
            'psa': [], 'psa_comment': None, 'rnci': None, 'rnci_comment': None, 'ratp': None, 'ratp_comment': None,
            'ra': None, 'ra_comment': None, 'ee': None, 'ee_comment': None, 'nst': None, 'nst_comment': None,
            'nc': None, 'nc_comment': None, 'ps': None, 'ps_comment': None,
            'overall_reviewer_feedback': "I'll finish this later, BRB", 'status': 'DR'}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_patch_response_1)
        partial_data = {
            'nc': 1
        }
        expected_patch_response_1['nc'] = 1
        response = user_y_client.patch(url, partial_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_patch_response_1)

        # fill the answer with the user
        partial_data_2 = {
            'psa': [problem_statements[0].id, problem_statements[1].id, problem_statements[2].id],
            'ee': 2,
            'ra': 4,
            'nst': 1,
            'nc': 2,
            'nst_comment': 'Fun times',
            'status': ReviewScore.STATUS_COMPLETE,

        }
        response = user_y_client.post(url, partial_data_2, format="json")
        self.assertEqual(response.status_code, 200)
        # write partial managerial review
        review_data_partial = {'overall_reviewer_feedback': "Roger-roger"}
        url = reverse('portfolio-project-manager-review', kwargs={'pk': portfolio_review_id})
        response = self.user_3_client.patch(url, review_data_partial, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['overall_reviewer_feedback'], 'Roger-roger')
        # write managerial review
        review_data_complete = {
            'psa': [problem_statements[0].id, problem_statements[1].id, problem_statements[2].id],
            'rnci': 2,
            'ratp': 4,
            'ra': 5,
            'ee': 5,
            'nst': 5,
            'nc': 5,
            'ps': 5,
            'impact': 5,
            'scale_phase': 6,
            'overall_reviewer_feedback': "Roger-roger"
        }
        response = self.user_3_client.post(url, review_data_complete, format="json")
        self.assertEqual(response.status_code, 200)

        # delete ps[1]
        ps_ids_to_keep = set([problem_statements[0].id, problem_statements[2].id])
        problem_statements[1].delete()
        url = reverse('review-score-get-or-delete', kwargs={'pk': question_id_y})
        response = self.user_3_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()['psa']), ps_ids_to_keep)

        url = reverse('portfolio-project-manager-review', kwargs={'pk': portfolio_review_id})
        response = self.user_3_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()['psa']), ps_ids_to_keep)

        # approve the project
        url = reverse('portfolio-project-approve', kwargs={'pk': portfolio_id})
        project_data = {'project': [project_id]}
        response = self.user_3_client.post(url, project_data, format="json")
        self.assertEqual(response.status_code, 200)

        # try to delete ps[2]
        url = reverse("portfolio-update", kwargs={"pk": portfolio_id})
        update_data = {'problem_statements': [
            {'id': problem_statements[0].id,
             'name': problem_statements[0].name,
             'description': problem_statements[0].description}]
        }

        response = self.user_3_client.patch(url, update_data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()['detail'],
            f"Problem Statements linked to approved projects may not be deleted: [{problem_statements[1].id}]")
