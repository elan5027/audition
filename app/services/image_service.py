from starlette.datastructures import UploadFile
from app.clients.s3_client import S3Client


class ImageService:
    def __init__(
        self,
        s3_client: S3Client,
    ) -> None:
        self._s3_client = s3_client

    def create_presing(self, object_name: str, method: str):
        return self._s3_client.create_presigned_url(
            object_name=object_name, method=method
        )
