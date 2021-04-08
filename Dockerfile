# Use
FROM public.ecr.aws/lambda/python:3.8

COPY radarprocessor/ ./radarprocessor
COPY ./requirements-frozen.txt ./requirements-frozen.txt

RUN pip3 install -r requirements-frozen.txt
CMD ["radarprocessor/main.handler"]