from __future__ import print_function
from datadelivery.config import ConfigFile
from datadelivery.s3 import S3, NotFoundException

APP_NAME = "datadelivery"


class Commands(object):
    def __init__(self, version_str):
        self.version_str = version_str

    def _create_s3(self):
        config = ConfigFile().read_or_create_config()
        return S3(config, user_agent_str='{}/{}'.format(APP_NAME, self.version_str))

    def deliver(self, bucket_name, email, user_message, resend):
        """
        Deliver a bucket to a particular user with the user_message. When resend is True include force flag.
        :param bucket_name: str: name of the bucket to deliver
        :param email: str: email address of user to send the bucket to
        :param user_message: str: custom message to send in the delivery email
        :param resend: bool: is this a resend of an existing delivery
        """
        s3 = self._create_s3()
        to_user = s3.get_user_by_email(email)
        try:
            bucket = s3.get_bucket_by_name(bucket_name)
        except NotFoundException:
            bucket = s3.create_bucket(bucket_name)
        delivery = s3.create_delivery(bucket, to_user, user_message)
        s3.send_delivery(delivery, resend)
