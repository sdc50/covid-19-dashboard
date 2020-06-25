from subprocess import Popen


def load_jupyter_server_extension(nbapp):
    """serve the panel-app directory with bokeh server"""
    Popen(["panel", "serve", "panel_app", "--allow-websocket-origin=*"])
