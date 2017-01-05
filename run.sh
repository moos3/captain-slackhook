#!/bin/bash

sed -i "s|*SLACK_TOKEN =.*|SLACK_TOKEN = ${SLACK_TOKEN}|i" /srv/slackhook/.env
sed -i "s|*BOT_ID =.*|BOT_ID = ${BOT_ID}|i" /srv/slackhook/.env
sed -i "s|*BOT_NAME =.*|BOT_NAME = ${BOT_NAME}|i" /srv/slackhook/.env
sed -i "s|*AUTH_WEBHOOK_SECRET =.*|AUTH_WEBHOOK_SECRET = ${AUTH_WEBHOOK_SECRET}|i" /srv/slackhook/.env
sed -i "s|*HIPCHAT_API_TOKEN =.*|HIPCHAT_API_TOKEN = ${HIPCHAT_API_TOKEN}|i" /srv/slackhook/.env
sed -i "s|*HIPCHAT_API_HOST =.*|HIPCHAT_API_HOST = ${HIPCHAT_API_HOST}|i" /srv/slackhook/.env
sed -i "s|*INSTANCE_URL =.*|INSTANCE_URL = ${INSTANCE_URL}|i" /srv/slackhook/.env
sed -i "s|*BOT_USERNAME =.*|BOT_USERNAME = ${BOT_USERNAME}|i" /srv/slackhook/.env
sed -i "s|*DEBUG =.*|DBEUG = ${DEBUG}|i" /srv/slackhook/.env
sed -i "s|*DEFAULT_MIMETYPE =.*|DEFAULT_MIMETYPE = ${DEFAULT_MIMETYPE}|i" /srv/slackhook/.env
sed -i "s|*BOT_IMAGE_URL =.*|BOT_IMAGE_URL = ${BOT_IMAGE_URL}|i" /srv/slackhook/.env

cd /srv/slackhook
python main.py

