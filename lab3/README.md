In the outer Twidder folder use following commands to start server: <br />
export FLASK_APP=twidder <br />
export FLASK_DEBUG=true <br />
pip install -e . (Might need sudo for this one.) <br />
flask run <br />
WebSocket funkar inte med detta sättet så det är bättre att bara köra views.py :p