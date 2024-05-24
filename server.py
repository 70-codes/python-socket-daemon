import socket
import threading
import ssl
import logging
from config_handler import get_path
import time

HOST = socket.gethostbyname(socket.gethostname())
PORT = 46789


class Server:
    def __init__(self, config_file):
        """
        Initializes a new instance of the Server class with
        the given configuration file.

        Parameters:
            config_file (str): The path to the configuration file.

        Returns:
            None
        """
        self.config = self.load_config(config_file)
        self.host = HOST
        self.port = PORT
        self.ssl_enabled = int(self.config.get("ssl_enabled"))
        self.reread_on_query = int(self.config.get("REREAD_ON_QUERY"))
        self.file_path = self.config.get("linuxpath")
        self.file_contents = None
        if not self.reread_on_query:
            self.file_contents = self.read_file(self.file_path)
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def load_config(self, conf_file):
        """
        Load the configuration from the given configuration file.

        Parameters:
            conf_file (str): The path to the configuration file.

        Returns:
            dict: A dictionary containing the loaded configuration.
            The keys are the configuration keys and the values are
            the corresponding values.

        Raises:
            Exception: If there is an error loading the configuration file.
        """
        config = {}
        try:
            config["linuxpath"] = get_path(conf_file)
            self.file_path = config["linuxpath"]
            with open(conf_file, "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        config[key.strip()] = value.strip()
        except Exception as e:
            logging.error(f"Error loading config file: {e}")
        return config

    def read_file(self, path):
        """
        Reads the contents of a file and returns them as a list of lines.

        Parameters:
            path (str): The path to the file to be read.

        Returns:
            list: A list of lines from the file.
        """
        # reading the file contents and splitting them into lines
        with open(path, "r") as f:
            return f.read().splitlines()

    def handle_client(self, conn, addr):
        """
        Handle a client connection.

        Args:
            conn (socket.socket): The client socket connection.
            addr (tuple): The client address.

        Raises:
            Exception: If there is an error handling the client.

        Returns:
            None

        This function handles a client connection by receiving
        data from the client, processing the query, sending the
        response back to the client, and logging the query information.
        It uses the `process_query` method to process the received
        query and generates a response. The response is then sent
        back to the client using the `sendall` method. The execution
        time of the query is calculated and passed to the `log_query`
        method for logging.
        If an exception occurs during the handling of the client,
        it is logged with the client address and the exception message.
        Finally, the client socket connection is closed.
        """
        # connecting and receiving data from the client
        try:
            start_time = time.time()
            data = conn.recv(1024).decode().strip()
            response = self.process_query(data)
            conn.sendall(response.encode() + b"\n")
            end_time = time.time()
            self.log_query(data, addr, end_time - start_time)
        except Exception as e:
            logging.error(f"Error handling clinet{addr}: {e}")
        finally:
            conn.close()

    def process_query(self, query):
        """
        Process a query and check if it exists in the file contents.

        Parameters:
            query (str): The query to be processed.

        Returns:
            str: "STRING EXISTS" if the query is
            found in the file contents,
            "STRING NOT FOUND" otherwise.
        """
        # checking if the query exists in the
        # file contents using linear search algorithm

        if self.reread_on_query:
            file_contents = self.read_file(self.file_path)
        else:
            file_contents = self.file_contents
        # returing a message to the user if the query exists or not
        if query in file_contents:
            return "STRING EXISTS"
        else:
            return "STRING NOT FOUND"

    def log_query(self, query, addr, time_taken):
        """
        Logs the details of a query along with the
        client's IP address and execution time.

        Parameters:
            query (str): The query that was executed.
            addr (str): The IP address of the client.
            time_taken (float): The time taken to
            execute the query in seconds.

        Returns:
            None
        """

        log_msg = f"DEBUG: Query:{query}, IP: {addr}, EXecution time: {time_taken:.6f}s"
        logging.debug(log_msg)

    def start_server(self):
        """
        Starts the server and listens for incoming connections.

        This function creates a socket and binds it to the
        specified host and port. It then listens for incoming
        connections. If SSL is enabled, it creates an SSL
        context with the server certificate and key, and wraps
        the socket with the SSL context. Finally, it enters an
        infinite loop where it accepts incoming connections
        and starts a new thread to handle each client connection.

        Parameters:
            self (Server): The Server instance.

        Returns:
            None
        """

        # creating a socket and listening for incoming connections
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((self.host, self.port))
        server_sock.listen()

        # wrapping the socket with SSL if SSL is enabled
        if self.ssl_enabled:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            context.load_cert_chain(
                certfile="ssl.pem",
                keyfile="private.key",
            )
            server_sock = context.wrap_socket(
                server_sock,
                server_side=True,
            )
        logging.info(f"Server started on {self.host}:{self.port}")
        while True:
            conn, addr = server_sock.accept()
            threading.Thread(
                target=self.handle_client,
                args=(conn, addr),
            ).start()


if __name__ == "__main__":
    server = Server("config.ini")
    server.start_server()
