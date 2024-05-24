import socket
import ssl
import time

#initializing global variables
HOST = socket.gethostbyname(socket.gethostname())
PORT = 46789


class Search:
    def __init__(self, host, port, ssl_enabled=False):
        """
        Initializes a new instance of the Search class
        with the given host, port, and SSL configuration.

        Parameters:
            host (str): The host address to connect to.
            port (int): The port number to connect to.
            ssl_enabled (bool, optional): Whether to use
            SSL for the connection. Defaults to False.

        Returns:
            None
        """
        self.host = host
        self.port = port
        self.ssl_enabled = ssl_enabled
        self.context = None
        # chekiing is ssl is enabled and making the needed configurations
        if self.ssl_enabled:
            context = ssl.create_default_context()
            context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

    def send_query(self, query):
        """
        Sends a query to the server and returns the response along
        with the execution time.

        Args:
            query (str): The query to send to the server.

        Returns:
            tuple: A tuple containing the response from the server
            (str) and the execution time (float) in seconds.
        """

        start_time = time.time()
        with socket.create_connection((self.host, self.port)) as conn:
            # creating a secure socket ssock if ssl is enabled
            if self.ssl_enabled:
                with self.context.wrap_socket(
                    conn,
                    server_hostname=self.host,
                ) as ssock:
                    ssock.sendall(query.encode())
                    response = ssock.recv(1024).decode().strip()
            else:
                conn.sendall(query.encode())
                response = conn.recv(1024).decode().strip()
            end_time = time.time()
            exec_time = end_time - start_time
            return response, exec_time

    def run_query(self, query):
        """
        Run a query and print the response and execution time.

        Parameters:
            query (str): The query to be executed.

        Returns:
            None

        This function sends a query to the server using the `send_query`
        method and prints the query, response, and execution time.
        The `send_query` method is responsible for sending the query
        to the server and returning the response and execution time.

        Example usage:
        ```
        query_text = "7;0;21;16;0;22;4;0;"
        client.run_query(query_text)
        ```
        """

        response, exec_time = self.send_query(query)
        print(
            f"Query: {query} | Response: {response} | Execution time: {exec_time:.6f}s"
        )


if __name__ == "__main__":
    host = HOST
    port = PORT
    ssl_enabled = False
    client = Search(host=host, port=port, ssl_enabled=ssl_enabled)
    query = input("Enter the search string: ")
    client.run_query(query)
