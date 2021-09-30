from datetime import datetime

if __name__ == '__main__':
    import redis

    from . import config, create_app
    from admin_service.models import DB, Election, Vote

    app = create_app()
    DB.init_app(app)

    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    pubsub = r.pubsub()
    pubsub.subscribe(config.REDIS_VOTES_LIST)

    while True:
        msg = pubsub.get_message()
        try:
            id, poll_number = msg.split()
        except ValueError:
            continue

        now = datetime.utcnow()
        e = DB.session.query(Election).filter(
            Election.start <= now <= Election.end
        ).first()
        if not e:
            continue

        invalid = None
        if DB.session.query(Vote).get(id):
            invalid = "Duplicate ballot."

        vote = Vote(id, poll_number, invalid, election_id=e.id)
        DB.session.add(vote)
        DB.session.commit()
