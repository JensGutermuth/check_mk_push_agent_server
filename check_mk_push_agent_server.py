# -*- coding: utf-8 -*-

import os
import time

from redis import StrictRedis

from flask import Flask, abort, jsonify, request

LIFETIME = 90


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    Source of this class: http://flask.pocoo.org/snippets/35/

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask('check_mk_push_agent_server')
proxy_app = ReverseProxied(app)
redis = StrictRedis()


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
