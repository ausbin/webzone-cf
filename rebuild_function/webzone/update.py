import os
import boto3
import hashlib
from typing import Optional
from dataclasses import dataclass
from boto3.s3.transfer import TransferConfig

# Very important to keep this constant! Can't trust the default
CHUNK_SIZE = 1 << 23

@dataclass
class S3Object:
    key: str
    etag: Optional[str]
    visited: bool

# Based on https://stackoverflow.com/a/43819225/321301
def calc_etag(fp, chunk_size):
    chunk_hashes = []

    while True:
        chunk = fp.read(chunk_size)
        if not chunk:
            break
        chunk_hashes.append(hashlib.md5(chunk))

    if not chunk_hashes:
        return f'"{hashlib.md5(b"").hexdigest()}"'
    elif len(chunk_hashes) == 1:
        return f'"{chunk_hashes[0].hexdigest()}"'
    else:
        return f'"{hashlib.md5(b"".join(chunk_hash.digest() for chunk_hash in chunk_hashes)).hexdigest()}-{len(chunk_hashes)}"'

def push_to_s3(local_path, distrib_id, bucket_name, unique_id):
    transfer_cfg = TransferConfig(multipart_threshold=CHUNK_SIZE, multipart_chunksize=CHUNK_SIZE)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    # TODO: Works for now because my website has very few files, but long-term this is sus
    objects = {summary.object_key: S3Object(summary.object_key, summary.e_tag, False)
               for summary in bucket.objects.all()}

    # Tuples of (system path, S3 key)
    to_put = []

    # Now, walk the filesystem!
    top = True
    for path, dirs, files in os.walk(local_path):
        dir_ = '/'.join(os.path.relpath(path, local_path).strip(os.sep).split(os.sep))

        for file in files:
            if file == 'index.html' and not top:
                key = dir_ + '/'
            else:
                if dir_:
                    key = dir_ + '/' + file
                else:
                    key = file

            full_path = os.path.join(path, file)
            if key in objects:
                objects[key].visited = True

                # TODO: reuse this fd instead of close()ing it and open()ing it
                #       again later
                with open(full_path, 'rb') as fp:
                    new_etag = calc_etag(fp, CHUNK_SIZE)

                # TODO: what about false positives here? (harmless but can cost
                #       me major $$$ for too many invalidations). add a
                #       CloudWatch monitor?
                if new_etag != objects[key].etag:
                    to_put.append((full_path, key))
            else:
                to_put.append((full_path, key))

        top = False

    to_nuke = [obj.key for obj in objects if not obj.visited]

    if to_nuke:
        # TODO: would using VersionIds here prevent concurrent runs of this Lambda
        #       from massively trolling?
        bucket.delete_objects(Delete={'Objects': [{'Key': key} for key in to_nuke]})

    for full_path, key in to_put:
        bucket.upload_file(full_path, key, Config=transfer_cfg)

    # Now, finally, invalidate everyone!
    to_invalidate = to_nuke + [key for _, key in to_put]

    # Hack to also invalidate / when we update /index.html
    if 'index.html' in to_invalidate:
        to_invalidate.append('')

    cf = boto3.client('cloudfront')
    cf.create_invalidation(DistributionId=distrib_id, InvalidationBatch={
        'CallerReference': unique_id,
        'Paths': {
            'Quantity': len(to_invalidate),
            'Items': ['/' + key for key in to_invalidate]
        },
    })
