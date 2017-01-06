FROM alpine:3.4

ENV GIT_BRANCH=v2

RUN apk add --update --no-cache git bash python py-pip && mkdir -p /srv/slackhook
RUN git clone -b $GIT_BRANCH https://github.com/moos3/captain-slackhook.git /srv/slackhook
COPY run.sh /run.sh
RUN pip install --upgrade pip && pip install -r /srv/slackhook/requirements.txt
RUN rm -rf /var/cache/apk/* /var/tmp/* /tmp/* ~/.cache && cp /srv/slackhook/template.env /srv/slackhook/.env && chmod +x /run.sh

ENV DEBUG=True
ENV DEFAULT_MIMETYPE="application/json"
ENV INSTANCE_URL="localhost"
ENV SLACK_TOKEN='xoxb-slack-token'
ENV BOT_ID='bot-id'
ENV AUTH_WEBHOOK_SECRET='ghYHapu1yZ9PfK9'
ENV BOT_NAME='Capt SlackHook'
ENV BOT_IMAGE_URL='http://static8.comicvine.com/uploads/square_avatar/3/32238/627298-captain_hook_by_diznee4me.jpg'
ENV HIPCHAT_API_TOKEN='hipchat-token'
ENV HIPCHAT_API_HOST='api.hipchat.com'
ENV BOT_USERNAME = 'captainSlackHook'

EXPOSE 5000

CMD ["bash", "-c", "/run.sh"]
