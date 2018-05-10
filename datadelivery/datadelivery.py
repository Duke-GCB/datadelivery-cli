import requests


CONTENT_TYPE = 'application/json'


class DataDeliveryApi(object):
    def __init__(self, config, user_agent_str):
        self.config = config
        self.user_agent_str = user_agent_str
        self.current_endpoint = self._get_current_endpoint()
        self.current_s3user = self._get_current_s3user()

    def _build_url(self, url_suffix):
        return '{}{}'.format(self.config.url, url_suffix)

    def _build_headers(self):
        return {
            'user-agent': self.user_agent_str,
            'Authorization': 'Token {}'.format(self.config.token),
            'content-type': CONTENT_TYPE,
        }

    def _get_request(self, url_suffix):
        url = self._build_url(url_suffix)
        headers = self._build_headers()
        response = requests.get(url, headers=headers)
        self._check_response(response)
        return response.json()

    def _post_request(self, url_suffix, data):
        url = self._build_url(url_suffix)
        headers = self._build_headers()
        response = requests.post(url, headers=headers, json=data)
        self._check_response(response)
        return response.json()

    @staticmethod
    def _check_response(response):
        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise DDException(response.text)

    def _get_current_endpoint(self):
        """
        Find the S3Endpoint that matches config.endpoint_name
        :return: S3Endpoint
        """
        url_suffix = 's3-endpoints/?name={}'.format(self.config.endpoint_name)
        for endpoint_response in self._get_request(url_suffix):
            return S3Endpoint(endpoint_response)
        raise NotFoundException("No endpoint found for s3 url: {}".format(self.config.s3_url))

    def get_current_user(self):
        """
        Find the User that matches the current user under the endpoint
        :return: User
        """
        return User(self._get_request('users/current-user/'))

    def _get_current_s3user(self):
        user = self.get_current_user()
        return self.get_s3user_by_user(user)

    def get_s3user_by_user(self, user):
        """
        Fetch s3 user that has the current endpoint and user
        :param endpoint: S3Endpoint: the s3 service are we using
        :param user: User: user who we want to find a S3User for
        :return: S3User or NotFoundException
        """
        url_suffix = 's3-users/?endpoint={}&user={}'.format(self.current_endpoint.id, user.id)
        for endpoint_response in self._get_request(url_suffix):
            return S3User(endpoint_response)
        raise NotFoundException("No s3 user found for endpoint {} and user {}".format(
            self.current_endpoint.id, user.id))

    def get_s3user_by_email(self, email):
        """
        Fetch s3 user that has the current endpoint and email
        :param email: str: email address of user to fetch
        :return: S3User or NotFoundException
        """
        url_suffix = 's3-users/?endpoint={}&email={}'.format(self.current_endpoint.id, email)
        for endpoint_response in self._get_request(url_suffix):
            return S3User(endpoint_response)
        raise NotFoundException("No s3 user found with email {} at endpoint {}".format(
            email, self.current_endpoint.id))

    def get_bucket_by_name(self, bucket_name):
        """
        Return S3Bucket or None if not found
        :param bucket_name: str: name of the bucket
        :return: S3Bucket
        """
        url_suffix = 's3-buckets/?name={}'.format(bucket_name)
        items = self._get_request(url_suffix)
        if items:
            return S3Bucket(items[0])
        raise NotFoundException("No bucket found with name {}".format(bucket_name))

    def create_bucket(self, bucket_name):
        """
        Create bucket with specified params.
        :param bucket_name: str: name of the bucket
        :return: S3Bucket
        """
        data = {
            'name': bucket_name,
            'owner': self.current_s3user.id,
            'endpoint': self.current_endpoint.id,
        }
        return S3Bucket(self._post_request('s3-buckets/', data=data))

    def get_or_create_bucket(self, bucket_name):
        """
        Get existing bucket, if it doesn't exist create one and return it.
        :param bucket_name: str: name of the bucket
        :return: S3Bucket
        """
        try:
            return self.get_bucket_by_name(bucket_name)
        except NotFoundException:
            return self.create_bucket(bucket_name)

    def create_delivery(self, bucket, to_s3user, user_message):
        """
        Create delivery of bucket to to_user with user_message.
        Delivery will still need to be sent
        :param bucket: S3Bucket: bucket to deliver (should be owned by current user)
        :param to_s3user: S3User: user to send the bucket to
        :param user_message: str: message to send with the delivery
        :return: S3Delivery
        """
        data = {
            'bucket': bucket.id,
            'from_user': self.current_s3user.id,
            'to_user': to_s3user.id,
            'user_message': user_message
        }
        return S3Delivery(self._post_request('s3-deliveries/', data=data))

    def send_delivery(self, delivery, force=None):
        """
        Request the datadelivery service to process the delivery.
        :param delivery: S3Delivery: the delivery to process
        :param force: bool: set to True to allow resending
        :return: S3Delivery
        """
        url_suffix = 's3-deliveries/{}/send/'.format(delivery.id)
        if force:
            url_suffix += "?force=true"
        return S3Delivery(self._post_request(url_suffix, data={}))


class User(object):
    def __init__(self, data):
        self.id = data['id']
        self.username = data['username']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']


class S3Endpoint(object):
    def __init__(self, data):
        self.id = data['id']
        self.url = data['url']


class S3Bucket(object):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.owner = data['owner']
        self.endpoint = data['endpoint']


class S3User(object):
    def __init__(self, data):
        self.id = data['id']
        self.user = data['user']
        self.endpoint = data['endpoint']
        self.email = data['email']
        self.type = data['type']


class S3Delivery(object):
    def __init__(self, data):
        self.id = data['id']
        self.bucket = data['bucket']
        self.from_user = data['from_user']
        self.to_user = data['to_user']
        self.state = data['state']
        self.user_message = data['user_message']
        self.decline_reason = data['decline_reason']
        self.performed_by = data['performed_by']
        self.delivery_email_text = data['delivery_email_text']


class NotFoundException(Exception):
    pass


class DDException(Exception):
    pass
