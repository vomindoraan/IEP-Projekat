if __name__ == '__main__':
    from datetime import datetime

    import redis

    from . import config, create_app
    from .models import DB, Election, Vote


    app = create_app()
    DB.init_app(app)

    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    pubsub = r.pubsub()
    pubsub.subscribe(config.REDIS_VOTES_LIST)

    while True:
        msg = pubsub.get_message()
        try:
            id, poll_number = msg.split()
        except (AttributeError, ValueError):
            continue

        now = datetime.now(config.TIMEZONE)
        e = Election.query.filter(Election.start <= now <= Election.end).first()
        if not e:
            continue

        invalid = None
        if Vote.query.get(id):
            invalid = "Duplicate ballot."

        vote = Vote(id, poll_number, invalid, election_id=e.id)
        DB.session.add(vote)
        DB.session.commit()
