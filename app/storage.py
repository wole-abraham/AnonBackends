import boto3
import os
from typing import List
import dotenv
import uuid
dotenv.load_dotenv()

ACCOUNT_ID = os.getenv("CLOUD_ACCOUNT_ID")
ACCESS_KEY = os.getenv("CLOUD_ACCESS_KEY")
SECRET_ACCESS_KEY=os.getenv("CLOUD_SECRET_ACCESS")
BUCKET_NAME=os.getenv("BUCKET_NAME")


def create_storage():
        
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=f"{ACCESS_KEY}",
        aws_secret_access_key=f"{SECRET_ACCESS_KEY}",
        region_name="auto"
    )
    return s3

class Storage():
    def __init__(self):
        self.s3 = create_storage()

    async def upload_doc(self, user, files):
        uploaded_file=[]
        for file in files:
            key = f"users/{user}/{uuid4()}"
            self.s3.put_object(
                Bucket=os.getenv("BUCKET_NAME"),
                Key=key,
                Body= await file.read(),
                ContentType=file.content_type
            )
            uploaded_file.append(key)
        return uploaded_file
    
    def generate_upload_url(self, count: int=1):
        url = {}
        for n in range(count):
            object_key = f"users/{uuid.uuid4()}"
            key = self.s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": os.getenv("BUCKET_NAME"),
                "Key": object_key,
            }
        , ExpiresIn=300,
        )
            url[object_key] = key
        return url

    
    def generate_download_url(self, object_key: List[str]):
        download_url = []
        for url in object_key:
            download_url.append(self.s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": os.getenv("BUCKET_NAME"),
                "Key": url,
            }
        ))
        return download_url
    

