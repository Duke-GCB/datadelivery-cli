from __future__ import print_function, absolute_import
import os
from datadelivery.config import ConfigFile
from datadelivery.datadelivery import DataDeliveryApi, NotFoundException

APP_NAME = "datadelivery"


class Commands(object):
    def __init__(self, version_str):
        self.version_str = version_str
        self._dd_api = None

    @property
    def dd_api(self):
        if not self._dd_api:
            self._dd_api = self._create_data_delivery_api()
        return self._dd_api

    def _create_data_delivery_api(self):
        config = ConfigFile().read_or_create_config()
        return DataDeliveryApi(config, user_agent_str='{}/{}'.format(APP_NAME, self.version_str))

    def deliver(self, bucket_name, email, user_message, resend):
        """
        Deliver a bucket to a particular user with the user_message. When resend is True include force flag.
        :param bucket_name: str: name of the bucket to deliver
        :param email: str: email address of user to send the bucket to
        :param user_message: str: custom message to send in the delivery email
        :param resend: bool: is this a resend of an existing delivery
        """
        to_s3user = self.dd_api.get_s3user_by_email(email)
        bucket = self.dd_api.get_or_create_bucket(bucket_name)
        delivery = self.dd_api.create_delivery(bucket, to_s3user, user_message)
        self.dd_api.send_delivery(delivery, resend)

    def upload(self, bucket_name, file_folder_paths):
        """
        Upload files/folders to a bucket
        :param bucket_name: str: name of the bucket to upload into
        :param file_folder_paths: [str]: list of paths to upload
        """
        pass


class CommandUtil(object):
    @staticmethod
    def get_file_paths(path):
        result = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                result.append(os.path.join(root, filename))
        return result
