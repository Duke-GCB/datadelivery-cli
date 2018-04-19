from __future__ import print_function
from datadelivery.config import ConfigFile
from datadelivery.s3 import S3

APP_NAME = "datadelivery"


class Commands(object):
    @staticmethod
    def _create_s3():
        config = ConfigFile().read_or_create_config()
        return S3(config, user_agent_str='datadelivery/0.0.1')

    def deliver(self, bucket_name, email, user_message):
        s3 = self._create_s3()
        to_user = s3.get_user_by_email(email)
        bucket = s3.get_bucket_by_name(bucket_name)
        if not bucket:
            bucket = s3.create_bucket(bucket_name)
        delivery = s3.create_delivery(bucket, to_user, user_message)
        print(s3.send_delivery(delivery))
