from network import server


def main():
    server_instance = server.AsyncServer()
    server_instance.run()

if __name__ == "__main__":
    main()