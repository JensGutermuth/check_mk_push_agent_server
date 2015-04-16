# -*- coding: utf-8 -*-

import os
import time

from redis import StrictRedis

from flask import Flask, abort, jsonify, request

app = Flask('check_mk_push_agent_server')
redis = StrictRedis()

LIFETIME = 90


def load_tokens():
    with open(os.environ['TOKEN_FILE']) as token_file:
        for line in token_file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            token, hostname = line.split()
            yield token, hostname


@app.route('/push/<token>', methods=["POST"])
def push(token):
    """Push check_mk_agent data."""
    tokens = dict(load_tokens())
    if token not in tokens:
        abort(404)
    hostname = tokens[token]
    redis.set(
        ':'.join(['check_mk_push_agent', 'data', hostname]),
        request.data,
        ex=LIFETIME
    )
    redis.hset(
        'check_mk_push_agent:last_seen',
        hostname,
        time.time()
    )
    return jsonify(dict(status="ok"))

if __name__ == '__main__':
    app.run(debug=True)
