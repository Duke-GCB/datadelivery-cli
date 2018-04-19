from unittest import TestCase
from mock import MagicMock, patch, call
from datadelivery.s3 import S3, NotFoundException


class S3TestCase(TestCase):
    def setUp(self):
        self.config = MagicMock(endpoint_name='main_endpoint', d4s2_url='someurl/', token='secret')
        self.user_agent_str = 'tool/1.0'
        self.current_user_id = 456
        self.current_endpoint_id = 123
        self.current_endpoint_response = [
            {
                'id': 123,
                'url': 'http://somewhere.com'
            }
        ]
        self.current_user_response = {
            'id': self.current_user_id,
            'user': 1,
            'endpoint': self.current_endpoint_id,
            'email': 'joe@joe.com',
            'type': 'Normal'
        }
        self.expected_headers = {
            'user-agent': 'tool/1.0',
            'Authorization': 'Token secret',
            'content-type': 'application/json'
        }

    def setup_responses(self, mock_method, get_responses):
        get_side_effects = []
        for get_response in get_responses:
            mock_get_response = MagicMock()
            mock_get_response.json.return_value = get_response
            get_side_effects.append(mock_get_response)
        mock_method.side_effect = get_side_effects

    @patch('datadelivery.s3.requests')
    def test_constructor_finds_current_endpoint_and_user(self, mock_requests):
        self.setup_responses(mock_requests.get, [
            self.current_endpoint_response,
            self.current_user_response
        ])

        s3 = S3(self.config, self.user_agent_str)

        self.assertEqual(s3.current_endpoint.id, self.current_endpoint_id)
        self.assertEqual(s3.current_endpoint.url, 'http://somewhere.com')

        self.assertEqual(s3.current_user.id, self.current_user_id)
        self.assertEqual(s3.current_user.user, 1)
        self.assertEqual(s3.current_user.endpoint, self.current_endpoint_id)
        self.assertEqual(s3.current_user.email, 'joe@joe.com')
        self.assertEqual(s3.current_user.type, 'Normal')

        mock_requests.get.assert_has_calls([
            call('someurl/s3-endpoints/?name=main_endpoint', headers=self.expected_headers),
            call('someurl/s3-endpoints/123/current-user/', headers=self.expected_headers),
        ])

    @patch('datadelivery.s3.requests')
    def test_get_user_by_email(self, mock_requests):
        self.setup_responses(mock_requests.get, [
            self.current_endpoint_response,
            self.current_user_response,
            [
                {
                    'id': 789,
                    'user': 2,
                    'endpoint': 123,
                    'email': 'bob@bob.com',
                    'type': 'Normal'
                }
            ]
        ])

        s3 = S3(self.config, self.user_agent_str)
        s3_user = s3.get_user_by_email('bob@bob.com')

        self.assertEqual(s3_user.id, 789)
        self.assertEqual(s3_user.user, 2)
        self.assertEqual(s3_user.endpoint, self.current_endpoint_id)
        self.assertEqual(s3_user.email, 'bob@bob.com')
        self.assertEqual(s3_user.type, 'Normal')

        mock_requests.get.assert_has_calls([
            call('someurl/s3-users/?email=bob@bob.com', headers=self.expected_headers),
        ])

    @patch('datadelivery.s3.requests')
    def test_get_user_by_email_not_found(self, mock_requests):
        self.setup_responses(mock_requests.get, [
            self.current_endpoint_response,
            self.current_user_response,
            []
        ])

        s3 = S3(self.config, self.user_agent_str)
        with self.assertRaises(NotFoundException):
            s3.get_user_by_email('tom@tom.com')

        mock_requests.get.assert_has_calls([
            call('someurl/s3-users/?email=tom@tom.com', headers=self.expected_headers),
        ])

    @patch('datadelivery.s3.requests')
    def test_get_bucket_by_name(self, mock_requests):
        self.setup_responses(mock_requests.get, [
            self.current_endpoint_response,
            self.current_user_response,
            [
                {
                    'id': 444,
                    'name': 'some_bucket',
                    'owner': 2,
                    'endpoint': self.current_endpoint_id
                }
            ]
        ])

        s3 = S3(self.config, self.user_agent_str)
        s3_bucket = s3.get_bucket_by_name('some_bucket')

        self.assertEqual(s3_bucket.id, 444)
        self.assertEqual(s3_bucket.name, 'some_bucket')
        self.assertEqual(s3_bucket.owner, 2)
        self.assertEqual(s3_bucket.endpoint, self.current_endpoint_id)

        mock_requests.get.assert_has_calls([
            call('someurl/s3-buckets/?name=some_bucket', headers=self.expected_headers),
        ])

    @patch('datadelivery.s3.requests')
    def test_get_bucket_by_name_not_found(self, mock_requests):
        self.setup_responses(mock_requests.get, [
            self.current_endpoint_response,
            self.current_user_response,
            []
        ])

        s3 = S3(self.config, self.user_agent_str)
        with self.assertRaises(NotFoundException):
            s3.get_bucket_by_name('otherBucket')

        mock_requests.get.assert_has_calls([
            call('someurl/s3-buckets/?name=otherBucket', headers=self.expected_headers),
        ])

    @patch('datadelivery.s3.requests')
    def test_create_bucket(self, mock_requests):
        self.setup_responses(mock_requests.get, [
            self.current_endpoint_response,
            self.current_user_response,
        ])
        self.setup_responses(mock_requests.post, [
            {
                'id': 333,
                'name': 'mybucket',
                'owner': self.current_user_id,
                'endpoint': self.current_endpoint_id
            }
        ])

        s3 = S3(self.config, self.user_agent_str)
        s3_bucket = s3.create_bucket('mybucket')

        self.assertEqual(s3_bucket.id, 333)
        self.assertEqual(s3_bucket.name, 'mybucket')
        self.assertEqual(s3_bucket.owner, self.current_user_id)
        self.assertEqual(s3_bucket.endpoint, self.current_endpoint_id)

        expected_json = {
            'owner': self.current_user_id,
            'endpoint': self.current_endpoint_id,
            'name': 'mybucket'
        }
        mock_requests.post.assert_has_calls([
            call('someurl/s3-buckets/', headers=self.expected_headers, json=expected_json),
        ])

    @patch('datadelivery.s3.requests')
    def test_create_delivery_and_send(self, mock_requests):
        self.setup_responses(mock_requests.get, [
            self.current_endpoint_response,
            self.current_user_response,
        ])
        self.setup_responses(mock_requests.post, [
            {
                'id': 888,
                'bucket': 222,
                'from_user': self.current_user_id,
                'to_user': 444,
                'state': 0,
                'user_message': 'Testing',
                'decline_reason': '',
                'performed_by': '',
                'delivery_email_text': '',
            }
        ])

        s3 = S3(self.config, self.user_agent_str)
        s3_delivery = s3.create_delivery(
            bucket=MagicMock(id=222),
            to_user=MagicMock(id=444),
            user_message='Testing'
        )

        self.assertEqual(s3_delivery.id, 888)
        self.assertEqual(s3_delivery.bucket, 222)
        self.assertEqual(s3_delivery.from_user, self.current_user_id)
        self.assertEqual(s3_delivery.to_user, 444)
        self.assertEqual(s3_delivery.state, 0)
        self.assertEqual(s3_delivery.user_message, 'Testing')
        self.assertEqual(s3_delivery.decline_reason, '')
        self.assertEqual(s3_delivery.performed_by, '')
        self.assertEqual(s3_delivery.delivery_email_text, '')

        expected_json = {
            'bucket': 222,
            'from_user': self.current_user_id,
            'to_user': 444,
            'user_message': 'Testing',
        }
        mock_requests.post.assert_has_calls([
            call('someurl/s3-deliveries/', headers=self.expected_headers, json=expected_json),
        ])

    @patch('datadelivery.s3.requests')
    def test_send_delivery(self, mock_requests):
        self.setup_responses(mock_requests.get, [
            self.current_endpoint_response,
            self.current_user_response,
        ])
        self.setup_responses(mock_requests.post, [
            {
                'id': 888,
                'bucket': 222,
                'from_user': self.current_user_id,
                'to_user': 444,
                'state': 1,
                'user_message': 'Testing',
                'decline_reason': '',
                'performed_by': '',
                'delivery_email_text': '',
            }
        ])

        s3 = S3(self.config, self.user_agent_str)
        s3_delivery = s3.send_delivery(
            delivery=MagicMock(id=888)
        )

        self.assertEqual(s3_delivery.id, 888)
        self.assertEqual(s3_delivery.bucket, 222)
        self.assertEqual(s3_delivery.from_user, self.current_user_id)
        self.assertEqual(s3_delivery.to_user, 444)
        self.assertEqual(s3_delivery.state, 1)
        self.assertEqual(s3_delivery.user_message, 'Testing')
        self.assertEqual(s3_delivery.decline_reason, '')
        self.assertEqual(s3_delivery.performed_by, '')
        self.assertEqual(s3_delivery.delivery_email_text, '')

        mock_requests.post.assert_has_calls([
            call('someurl/s3-deliveries/888/send/', headers=self.expected_headers, json={}),
        ])

    @patch('datadelivery.s3.requests')
    def test_send_delivery_resend(self, mock_requests):
        self.setup_responses(mock_requests.get, [
            self.current_endpoint_response,
            self.current_user_response,
        ])
        self.setup_responses(mock_requests.post, [
            {
                'id': 888,
                'bucket': 222,
                'from_user': self.current_user_id,
                'to_user': 444,
                'state': 1,
                'user_message': 'Testing',
                'decline_reason': '',
                'performed_by': '',
                'delivery_email_text': '',
            }
        ])

        s3 = S3(self.config, self.user_agent_str)
        s3_delivery = s3.send_delivery(
            delivery=MagicMock(id=888),
            force=True
        )

        mock_requests.post.assert_has_calls([
            call('someurl/s3-deliveries/888/send/?force=true', headers=self.expected_headers, json={}),
        ])
