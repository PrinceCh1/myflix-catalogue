from flask import Flask
from microservices.user_service.app.routes import user_bp, authentication_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "05527cbaf81fadfb66a1ab0a5b68394bb20a8d00"
app.register_blueprint(user_bp, url_prefix="/users")
app.register_blueprint(authentication_bp)


if __name__ == "__main__":
    app.run(port=8000)
