"""
Web interface module for ModuLens.
"""

from flask import Flask

__all__ = ['app', 'create_app']

def create_app():
    """Create and configure the Flask app."""
    from modulens.web.app import create_app as _create_app
    return _create_app() 