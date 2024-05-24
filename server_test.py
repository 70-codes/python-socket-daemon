import pytest
from unittest.mock import patch, mock_open, MagicMock
from server import Server
import socket
import ssl


@pytest.fixture
def mock_config():
    """
    Fixture that returns a dictionary containing mock configuration values.

    Returns:
        dict: A dictionary with the following keys:
            - "linuxpath" (str): The path to a mock file.
            - "ssl_enabled" (str): The SSL enabled flag as a string.
            - "REREAD_ON_QUERY" (str): The REREAD_ON_QUERY flag as a string.
    """
    return {
        "linuxpath": "./200k.txt",
        "ssl_enabled": "1",
        "REREAD_ON_QUERY": "1",
    }


@pytest.fixture
def server_instance(mock_config):
    """
    Fixture that returns an instance of the Server class with
    the given mock configuration.

    Parameters:
        mock_config (dict): A dictionary containing mock configuration values.
            - "linuxpath" (str): The path to a mock file.
            - "ssl_enabled" (str): The SSL enabled flag as a string.
            - "REREAD_ON_QUERY" (str): The REREAD_ON_QUERY flag as a string.

    Returns:
        Server: An instance of the Server class with the given
        mock configuration.

    This fixture patches the "server.get_path" function and the "builtins.open"
    function to return the mock values specified in the mock_config dictionary.
    It then creates an instance of the Server class with the "config.ini"
    configuration file.

    Example usage:
    ```
    def test_server_instance(server_instance):
        assert isinstance(server_instance, Server)
        assert server_instance.config["linuxpath"] == "./200k.txt"
        assert server_instance.config["ssl_enabled"] == "0"
        assert server_instance.config["REREAD_ON_QUERY"] == "1"
    ```
    """
    with (
        patch("server.get_path", return_value=mock_config["linuxpath"]),
        patch(
            "builtins.open",
            mock_open(
                read_data="linuxpath=./200k.txt\nssl_enabled=0\nREREAD_ON_QUERY=1"
            ),
        ),
    ):
        return Server("config.ini")


def test_load_config(server_instance):
    """
    Test the load_config method of the server_instance object.

    This function tests the load_config method of the server_instance object by
    loading the configuration from the "config.ini" file and asserting that the
    values of the "linuxpath", "ssl_enabled", and "REREAD_ON_QUERY" keys in the
    config dictionary are as expected.

    Parameters:
        server_instance (Server): The server instance to test.

    Returns:
        None

    Raises:
        AssertionError: If the values of the "linuxpath", "ssl_enabled",
        or "REREAD_ON_QUERY" keys in the config dictionary are not as expected.
    """
    config = server_instance.load_config("config.ini")
    assert config["linuxpath"] == "./200k.txt"
    assert config["ssl_enabled"] == "0"
    assert config["REREAD_ON_QUERY"] == "1"


def test_read_file(server_instance):
    with patch("builtins.open", mock_open(read_data="line1\nline2\nline3")):
        contents = server_instance.read_file("/200k.txt")
        assert contents == ["line1", "line2", "line3"]


def test_process_query(server_instance):
    """
    Test the read_file method of the server_instance object.

    This function tests the read_file method of the server_instance object
    by mocking the builtin open function and verifying that the contents of
    the file are correctly read and returned as a list of lines.

    Parameters:
        server_instance (Server): The server instance to test.

    Returns:
        None

    Raises:
        AssertionError: If the contents of the
        file do not match the expected list of lines.
    """
    # Mock the read_file method if REREAD_ON_QUERY is enabled
    with patch.object(
        server_instance,
        "read_file",
        return_value=["test_query"],
    ):
        server_instance.reread_on_query = True
        response = server_instance.process_query("test_query")
        assert response == "STRING EXISTS"

        response = server_instance.process_query("other_query")
        assert response == "STRING NOT FOUND"

    # Use the preloaded file contents if REREAD_ON_QUERY is disabled
    server_instance.file_contents = ["test_query"]
    server_instance.reread_on_query = False
    response = server_instance.process_query("test_query")
    assert response == "STRING EXISTS"

    response = server_instance.process_query("other_query")
    assert response == "STRING NOT FOUND"


def test_handle_client(server_instance):
    """
    Test the handle_client method of the server_instance object.

    This function tests the handle_client method of the server_instance
    object by mocking the process_query and log_query methods. It creates
    a mock connection object with a mock recv method that returns the byte
    string "test_query\n". It then calls the handle_client method of the
    server_instance object with the mock connection and address
    ("127.0.0.1", 12345).
    It asserts that the mock_conn.sendall method is called once with the byte
    string "STRING EXISTS\n" and that the mock_conn.close
    method is called once.

    Parameters:
        server_instance (Server): The server instance to test.

    Returns:
        None
    """
    mock_conn = MagicMock()
    mock_conn.recv.return_value = b"test_query\n"
    with patch.object(
        server_instance, "process_query", return_value="STRING EXISTS"
    ), patch.object(server_instance, "log_query"):
        server_instance.handle_client(mock_conn, ("127.0.0.1", 12345))
        mock_conn.sendall.assert_called_once_with(b"STRING EXISTS\n")
        mock_conn.close.assert_called_once()


def test_start_server(server_instance):
    """
    Test the start_server method of the server_instance object.

    This function tests the start_server method of the server_instance
    object by mocking the socket, threading, and handle_client methods.
    It creates two sets of mock patches to simulate the behavior of the
    server when SSL is enabled and disabled. In both sets of patches, the
    server_instance.ssl_enabled attribute is set to the corresponding value,
    and the server_instance.start_server method is called. The patches
    are used to mock the creation of a socket, the creation of a thread,
    and the handling of a client connection. The mock_socket.accept method
    is also patched to return a mock connection and address.

    Parameters:
        server_instance (Server): The server instance to test.

    Returns:
        None
    """
    # Mock client connection
    mock_client_socket = MagicMock()

    with patch("socket.socket") as mock_socket, patch(
        "threading.Thread"
    ) as mock_thread, patch.object(
        server_instance, "handle_client"
    ) as mock_handle_client, patch.object(
        socket.socket, "accept", return_value=(mock_client_socket, ("127.0.0.1", 46789))
    ):

        # Mock the server socket instance
        mock_server_socket_instance = mock_socket.return_value
        mock_server_socket_instance.accept.return_value = (
            mock_client_socket,
            ("127.0.0.1", 46789),
        )

        # Run the server without SSL enabled
        server_instance.ssl_enabled = 0

        # We need to break the infinite loop in start_server for the test
        with patch("threading.Thread.start", side_effect=Exception("Thread started")):
            try:
                server_instance.start_server()
            except Exception as e:
                assert str(e) == "Thread started"

        # Verify the calls for non-SSL case
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_server_socket_instance.bind.assert_called_once_with(
            (server_instance.host, server_instance.port)
        )
        mock_server_socket_instance.listen.assert_called_once()
        mock_handle_client.assert_called_once_with(
            mock_client_socket, ("127.0.0.1", 46789)
        )

        # Run the server with SSL enabled
        server_instance.ssl_enabled = 1
        with patch.object(
            ssl.SSLContext, "wrap_socket", return_value=mock_server_socket_instance
        ):
            try:
                server_instance.start_server()
            except Exception as e:
                assert str(e) == "Thread started"

        # Verify the SSL-related calls
        mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_server_socket_instance.bind.assert_called_with(
            (server_instance.host, server_instance.port)
        )
        mock_server_socket_instance.listen.assert_called()
        mock_handle_client.assert_called_with(mock_client_socket, ("127.0.0.1", 46789))


if __name__ == "__main__":
    pytest.main()
