import uvicorn

from app.main import app


def main():
    # create and configure uvicorn.Server manually
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="info", reload=True)
    server = uvicorn.Server(config)

    # inject the server into app.state so lifespan can access it
    app.state.server = server

    # run server (blocking call)
    server.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stoped by Ctrl+C")