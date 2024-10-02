import boto3
import botocore
from botocore.exceptions import ClientError
from app.api.errors import http_error
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from fastapi import HTTPException


class S3Client:
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        bucket: str,
        aws_region: str,
    ) -> None:
        self._s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region,
            config=botocore.client.Config(
                max_pool_connections=50, signature_version="s3v4"
            ),
        )
        self._bucket = bucket

    def create_presigned_url(
        self, object_name: str, expiration=3600, method: str = "get_object"
    ):
        print("method : ", method)
        try:
            response = self._s3_client.generate_presigned_url(
                ClientMethod=method,
                Params={"Bucket": self._bucket, "Key": object_name},
                ExpiresIn=expiration,
            )
            return response

        except (NoCredentialsError, PartialCredentialsError):
            raise HTTPException(status_code=400, detail="Credentials not found")

    def list_images_in_s3_folder(self, folder_name):
        # 폴더 내 모든 객체 나열
        response = self._s3_client.list_objects_v2(
            Bucket=self._bucket, Prefix=folder_name
        )

        # 파일 목록 추출
        if "Contents" in response:
            images = [
                content["Key"]
                for content in response["Contents"]
                if content["Key"].endswith((".png", ".jpg", ".jpeg", ".gif"))
            ]
            return images
        else:
            return []
