from flask import Flask

from devdigest.feed.views import feed_blueprint


app = Flask('devdigest', static_folder='site_media')
app.register_blueprint(feed_blueprint)
