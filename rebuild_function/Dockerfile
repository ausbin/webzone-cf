# From https://docs.aws.amazon.com/lambda/latest/dg/images-create.html#images-create-from-base

FROM public.ecr.aws/lambda/python:3.9-arm64

RUN curl -L "https://github.com/gohugoio/hugo/releases/download/v0.109.0/hugo_0.109.0_linux-arm64.tar.gz" | tar -C /usr/local/bin -zx hugo

RUN yum update -y && \
    yum install -y git \
    yum clean all

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY webzone/ ${LAMBDA_TASK_ROOT}
