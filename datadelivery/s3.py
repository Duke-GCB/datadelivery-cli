import requests


CONTENT_TYPE = 'application/json'


class S3(object):
    def __init__(self, config, user_agent_str):
        self.config = config
        self.user_agent_str = user_agent_str
        self.current_endpoint = self._get_current_endpoint()
        self.current_user = self._get_current_user_for_endpoint(self.current_endpoint)

    def _build_url(self, url_suffix):
        return '{}{}'.format(self.config.d4s2_url, url_suffix)

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
            raise S3Exception(response.text)

    def _get_current_endpoint(self):
        """
        Find the S3Endpoint that matches config.endpoint_name
        :return: S3Endpoint
        """
        url_suffix = 's3-endpoints/?name={}'.format(self.config.endpoint_name)
        for endpoint_response in self._get_request(url_suffix):
            return S3Endpoint(endpoint_response)
        raise NotFoundException("No endpoint found for s3 url: {}".format(self.config.s3_url))

    def _get_current_user_for_endpoint(self, endpoint):
        """
        Find the S3User that matches the current user
        :return: S3User
        """
        url_suffix = 's3-endpoints/{}/current-user/'.format(endpoint.id)
        return S3User(self._get_request(url_suffix))

    def get_user_by_email(self, email):
        for endpoint_response in self._get_request('s3-users/?email={}'.format(email)):
            return S3User(endpoint_response)
        raise NotFoundException("No user found with email {}".format(email))

    def get_bucket_by_name(self, bucket_name):
        """
        Return S3Bucket or None if not found
        :param bucket_name: str: name of the bucket
        :return: S3Bucket
        """
        url_suffix = 's3-buckets/?name={}'.format(bucket_name)
        return S3Bucket(self._get_request(url_suffix)[0])

    def create_bucket(self, bucket_name):
        """
        Create bucket with specified params.
        :param bucket_name: str: name of the bucket
        :return: S3Bucket
        """
        data = {
            'name': bucket_name,
            'owner': self.current_user.id,
            'endpoint': self.current_endpoint.id,
        }
        return S3Bucket(self._post_request('s3-buckets/', data=data))

    def create_delivery(self, bucket, to_user, user_message):
        """
        Create delivery of bucket to to_user with user_message.
        Delivery will still need to be sent
        :param bucket: S3Bucket: bucket to deliver (should be owned by current user)
        :param to_user: S3User: user to send the bucket to
        :param user_message: str: message to send with the delivery
        :return: S3Delivery
        """
        data = {
            'bucket': bucket.id,
            'from_user': self.current_user.id,
            'to_user': to_user.id,
            'user_message': user_message
        }
        return S3Delivery(self._post_request('s3-deliveries/', data=data))

    def send_delivery(self, delivery):
        url_suffix = 's3-deliveries/{}/send/'.format(delivery.id)
        return S3Delivery(self._post_request(url_suffix, data={}))


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


class S3Exception(Exception):
    pass
