# Server component of a push agent setup for check_mk

Use the wsgi application in `check_mk_push_agent_server:app` to receive the
outputs from `check_mk_agent`. Each host is identified by a token, which also
serves as authentication for it. The push agent for the monitored host is in the
[check_mk_push_agent](https://github.com/Delphinator/check_mk_push_agent) repo.

Use the `fetch.py` script with the hostname as first command line argument
as a datasource programm in check_mk.

Configuration is done via environment variables:
- `TOKEN_FILE`: File to read the token - hostname pairs from.

   Empty lines and lines starting with `#` are ignored. Seperate the token
   and the hostname with whitespace. The token is alphanumeric.
