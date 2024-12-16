#!/bin/bash
gunicorn --workers 8 path.to.pyfile:application