from flask import Flask, request, redirect, url_for, render_template
import boto3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# S3 Configuration from environment
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_KEY = os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("S3_ACCESS_KEY")
S3_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY") or os.environ.get("S3_SECRET_KEY")
S3_REGION = os.environ.get("AWS_REGION", "ap-south-1")

# Initialize boto3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET,
    region_name=S3_REGION
)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        file_name = request.form['file_name']

        if file and file_name:
            # Create safe file name (user input + keep original extension)
            file_name = secure_filename(file_name) + os.path.splitext(file.filename)[1]

            # Upload to S3 (make public)
            s3.upload_fileobj(file, S3_BUCKET, file_name, ExtraArgs={"ACL": "public-read"})

        return redirect(url_for('index'))

    # List all objects in bucket
    objects = s3.list_objects_v2(Bucket=S3_BUCKET).get('Contents', [])
    image_urls = [
        f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{obj['Key']}"
        for obj in objects
    ]

    return render_template('index.html', image_urls=image_urls)

@app.route('/gallery')
def gallery():
    objects = s3.list_objects_v2(Bucket=S3_BUCKET).get('Contents', [])
    image_urls = [
        f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{obj['Key']}"
        for obj in objects
    ]

    html = "".join([f'<img src="{url}" alt="Image">' for url in image_urls])
    return html

if __name__ == '__main__':
    # Only for local dev. In Docker, Gunicorn runs it.
    app.run(debug=True, host="0.0.0.0", port=5000)
