def init_routes(app):
    from .conversation_routes import bp as conv_bp
    from .ai_routes import bp as ai_bp

    app.register_blueprint(conv_bp, url_prefix='/api/conversation')  # đăng ký route conversation ở địa chỉ /api/conversation
    app.register_blueprint(ai_bp, url_prefix='/api/v1/ai')  # đăng ký route AI ở địa chỉ /api/v1/ai (prefix đã có trong Blueprint)
