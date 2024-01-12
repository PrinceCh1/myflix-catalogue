from flask import Flask
from microservices.video_service.app.routes import video_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "05527cbaf81fadfb66a1ab0a5b68394bb20a8d00"
app.register_blueprint(video_bp, url_prefix="/videos/")


if __name__ == "__main__":
    app.run(port=8000)