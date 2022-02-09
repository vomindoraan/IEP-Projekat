if __name__ == '__main__':
    from datetime import datetime
    from uuid import UUID

    import redis

    from . import config, create_app
    from .models import DB, Election, Participant, Vote


    app = create_app()
    DB.init_app(app)

    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    pubsub = r.pubsub()
    pubsub.subscribe(config.REDIS_VOTES_LIST)

    while True:
        msg = pubsub.get_message(ignore_subscribe_messages=True)
        try:
            values = msg['data'].decode('utf-8').split()
            ballot_uuid = UUID(values[0])
            poll_number = int(values[1])
        except (KeyError, TypeError, AttributeError, UnicodeDecodeError):
            continue

        with app.app_context():
            now = datetime.now(config.TIMEZONE)
            e = (
                Election.query
                .filter(Election.start <= now, now <= Election.end)
                .first()  # TODO: What if there are multiple elections?
            )
            if not e:
                continue

            invalid = None
            if Vote.query.filter(Vote.ballot_uuid == ballot_uuid).first():
                invalid = "Duplicate ballot."
            elif not (
                Participant.query
                .filter(Participant.election_id == e.id,
                        Participant.poll_number == poll_number)
                .first()
            ):
                invalid = "Invalid poll number."

            vote = Vote(ballot_uuid=ballot_uuid, poll_number=poll_number,
                        invalid=invalid, election_id=e.id)
            DB.session.add(vote)
            DB.session.commit()
