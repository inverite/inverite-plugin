from django.test import TestCase
from django.test import Client
from django.urls import reverse
from mock import patch


class TestViews(TestCase):
    guid = 'F7E5CF18-17F7-11E8-B859-8EAF463F2BE4'
    job_id = 'F7E5CF18-17F7-11E8-B859-8EAF463F2BE5'

    def create_patch(self, name):
        patcher = patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def setUp(self):
        self.mock_fetch_session_status = \
            self.create_patch(
                'inverite.fetch_session_status')
        self.mock_fetch_banks = \
            self.create_patch('inverite.fetch_banks')
        self.mock_fetch_bankform = \
            self.create_patch('inverite.fetch_bankform')
        self.mock_session_start = \
            self.create_patch('inverite.session_start')
        self.mock_fetch_session_status = \
            self.create_patch(
                'inverite.fetch_session_status')
        self.mock_provide_challenge_response = \
            self.create_patch(
                'inverite.provide_challenge_response')
        self.client = Client()

    def test_request_guid(self):
        response = self.client.get(
            reverse('request_guid', kwargs={'guid': TestViews.guid}))
        self.assertEqual(response.status_code, 302)

    def test_session_status_bad_api(self):
        self.mock_fetch_session_status.return_value = {}
        response = self.client.get(
            reverse(
                'session_status', kwargs={
                    'guid': 'F7E5CF18-17F7-11E8-B859-8EAF463F2BE4',
                    'bankID': '1',
                    'job_id': 'asdf'}))
        self.assertEqual(response.status_code, 200)

    def test_session_status_working(self):
        self.mock_fetch_session_status.return_value = {'status': 'working'}
        response = self.client.get(
            reverse(
                'session_status', kwargs={
                    'guid': TestViews.guid,
                    'bankID': '1',
                    'job_id': TestViews.job_id}))
        self.assertEqual(response.status_code, 200)

    def test_session_status_login_required(self):
        self.mock_fetch_session_status.return_value = {
            'status': 'login_required'}
        response = self.client.get(reverse('session_status', kwargs={
                                   'guid': TestViews.guid,
                                   'bankID': '1', 'job_id': TestViews.job_id}))
        self.assertEqual(response.status_code, 200)

    def test_session_status_authfail(self):
        self.mock_fetch_session_status.return_value = {'status': 'authfail'}
        response = self.client.get(reverse('session_status', kwargs={
                                   'guid': TestViews.guid,
                                   'bankID': '1', 'job_id': TestViews.job_id}))
        self.assertEqual(response.status_code, 200)

    def test_session_status_need_input(self):
        self.mock_fetch_session_status.return_value = {'status': 'need_input'}
        response = self.client.get(reverse('session_status', kwargs={
                                   'guid': TestViews.guid,
                                   'bankID': '1', 'job_id': TestViews.job_id}))
        self.assertEqual(response.status_code, 200)

    def test_session_status_need_image_coordinate_input(self):
        self.mock_fetch_session_status.return_value = {
            'status': 'need_image_coordinate_input'}
        response = self.client.get(reverse('session_status', kwargs={
                                   'guid': TestViews.guid,
                                   'bankID': '1', 'job_id': TestViews.job_id}))
        self.assertEqual(response.status_code, 200)

    def test_session_status_success(self):
        self.mock_fetch_session_status.return_value = {'status': 'success'}
        response = self.client.get(reverse('session_status', kwargs={
                                   'guid': TestViews.guid,
                                   'bankID': '1', 'job_id': TestViews.job_id}))
        self.assertEqual(response.status_code, 200)

    def test_session_status_json(self):
        self.mock_fetch_session_status.return_value = {'status': 'success'}
        response = self.client.get(reverse('session_status_json', kwargs={
                                   'guid': TestViews.guid,
                                   'bankID': '1', 'job_id': TestViews.job_id}))
        self.assertDictEqual(response.json(), {'status': 'success'})

    def test_choose_bank(self):
        self.mock_fetch_session_status.return_value = {'status': 'success'}
        response = self.client.get(
            reverse('choose_bank', args=(TestViews.guid,)))
        self.assertEqual(response.status_code, 200)

    def test_bank_form(self):
        self.mock_fetch_bankform.return_value = [
            {'name': 'username',
             'type': 'Text',
             'label': 'Account Number'},
            {'name': 'password',
             'type': 'Password',
             'label': 'Password'}
        ]
        response = self.client.get(
            reverse('bank_form', args=(TestViews.guid, 1)))
        self.assertEqual(response.status_code, 200)

    def test_bank_form_status(self):
        response = self.client.get(
            reverse('bank_form_status', args=(TestViews.guid, 1, 'authfail')))
        self.assertEqual(response.status_code, 200)

    def test_provide_challenge_response(self):
        response = self.client.get(reverse(
            'provide_challenge_response', args=(TestViews.guid, 1, TestViews.job_id)))  # noqa
        self.assertEqual(response.status_code, 302)
