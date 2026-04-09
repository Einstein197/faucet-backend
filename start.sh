#!/bin/bash
uvicorn ad_backend:app --host 0.0.0.0 --port $PORT
