import boto3
from botocore.exceptions import NoCredentialsError


def upload_to_s3_bucket(file_data, bucket_name, s3_file):
    s3 = boto3.client('s3')

    try:
        s3.upload_fileobj(file_data, bucket_name, s3_file)
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_file
            },
            ExpiresIn=24 * 3600
        )

        print("Upload Successful", url)
        return url
    except FileNotFoundError:
        print("The file was not found")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None

