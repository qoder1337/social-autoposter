from flask import Blueprint, request, render_template, redirect, url_for


base_bp = Blueprint(
    "base",
      __name__,
      url_prefix=None
    )

@base_bp.route('/', methods=['GET', 'POST'])
def index():
    return {"message": "hello WORLDY"}
