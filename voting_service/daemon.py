from zoneinfo import ZoneInfo


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
            user_jmbg = values[2]
        except (KeyError, TypeError, AttributeError, UnicodeDecodeError):
            continue

        with app.app_context():
            print(values, end="\t")

            now = datetime.now(ZoneInfo('Europe/Belgrade'))  # TODO
            e = (
                Election.query
                .filter(Election.start <= now, now <= Election.end)
                .first()  # TODO: What if there are multiple concurrent elections?
            )
            if not e:
                print("No ongoing election")
                continue

            invalid = None
            if Vote.query.filter_by(ballot_uuid=ballot_uuid).first():
                invalid = "Duplicate ballot."
            elif not (
                Participant.query
                .filter_by(election_id=e.id, poll_number=poll_number)
                .first()
            ):
                invalid = "Invalid poll number."

            print(invalid or "")

            vote = Vote(ballot_uuid=ballot_uuid, poll_number=poll_number,
                        user_jmbg=user_jmbg, invalid=invalid, election_id=e.id)
            DB.session.add(vote)
            DB.session.commit()
