import time
import csv


def linear_search(file_contents, query):
    """
    Checks if a given query exists in a list of
    file contents using a linear search algorithm.

    Parameters:
        file_contents (list): A list of strings
        representing the contents of a file.
        query (str): The string to search for in the file contents.

    Returns:
        bool: True if the query is found in the file contents, False otherwise.
    """
    # Check if the query is in the file contents
    return query in file_contents


def binary_search(file_contents, query):
    """
    Performs a binary search on a sorted list of file contents
    to find if a query exists.

    Args:
        file_contents (list): A sorted list of strings representing
        the contents of a file. query (str): The string to search
        for in the file contents.

    Returns:
        bool: True if the query is found in the file contents, False otherwise.
    """
    # Sort the file contents then check if the query is in the file contents
    file_contents.sort()
    low, high = 0, len(file_contents) - 1
    while low <= high:
        mid = (low + high) // 2
        if file_contents[mid] == query:
            return True
        elif file_contents[mid] < query:
            low = mid + 1
        else:
            high = mid - 1
    return False


def hash_table_search(file_contents, query):
    """
    Checks if a given query exists in a list
    of file contents using a hash table.

    Parameters:
        file_contents (list): A list of strings
        representing the contents of a file.
        query (str): The string to search for in the file contents.

    Returns:
        bool: True if the query is found in the file contents, False otherwise.
    """
    # Create a hash table of the file contents then
    # check if the query is in the file contents
    file_set = set(file_contents)
    return query in file_set


def boyer_moore_search(file_contents, query):
    """
    Searches for a given query string in a list
    of file contents using the Boyer-Moore algorithm.

    Args:
        file_contents (List[str]): A list of strings
        representing the contents of a file.
        query (str): The string to search for in the file contents.

    Returns:
        bool: True if the query is found in the file contents, False otherwise.
    """

    # Preprocess the pattern
    def preprocess(pattern):
        skip = {}
        for i in range(len(pattern)):
            skip[pattern[i]] = max(1, len(pattern) - i - 1)
        return skip

    # Search for the pattern in the file contents
    pattern = query
    skip = preprocess(pattern)
    for text in file_contents:
        m = len(pattern)
        n = len(text)
        i = m - 1
        while i < n:
            j = m - 1
            while j >= 0 and text[i] == pattern[j]:
                i -= 1
                j -= 1
            if j < 0:
                return True
            i += skip.get(text[i], m)
    return False


def kmp_search(file_contents, query):
    """
    Searches for a given query string in a list of file
    contents using the Knuth-Morris-Pratt algorithm.

    Args:
        file_contents (List[str]): A list of strings
        representing the contents of a file.
        query (str): The string to search for in the file contents.

    Returns:
        bool: True if the query is found in the file contents, False otherwise.
    """

    # Create the table and search for the pattern in the file contents
    def kmp_table(pattern):
        table = [0] * len(pattern)
        j = 0
        for i in range(1, len(pattern)):
            if pattern[i] == pattern[j]:
                j += 1
                table[i] = j
            else:
                if j != 0:
                    j = table[j - 1]
                    i -= 1
                else:
                    table[i] = 0
        return table

    pattern = query
    for text in file_contents:
        m = len(pattern)
        n = len(text)
        table = kmp_table(pattern)
        i = j = 0
        while i < n:
            if pattern[j] == text[i]:
                i += 1
                j += 1
            if j == m:
                return True
            elif i < n and pattern[j] != text[i]:
                if j != 0:
                    j = table[j - 1]
                else:
                    i += 1
    return False


def benchmark_algorithms(path, query):
    """
    Benchmarks the performance of different algorithms for
    searching a query in a file.

    Args:
        path (str): The path to the file containing the data to be searched.
        query (str): The query to search for in the file.

    Returns:
        dict: A dictionary containing the execution time of each algorithm.
        The keys are the names of the algorithms
              ("linear_search" and "binary_search") and the values
              are the execution times in seconds.

    Raises:
        FileNotFoundError: If the file specified by `path` does not exist.

    """
    try:
        with open(path, "r") as file:
            file_contents = file.read().splitlines()
            # Create a dictionary of algorithms to benchmark
            algorithms = {
                "linear_search": linear_search,
                "binary_search": binary_search,
                "kmp_search": kmp_search,
                # "boyer_moore_search": boyer_moore_search,
                # "hash_table_search": hash_table_search,
                # The two algorithms above have been commented
                # out to prevent their
                # execution as they consume a lot of time making them not to
                # be considered as an option
            }

            # Benchmark the algorithms
            results = {}
            for name, func in algorithms.items():
                start_time = time.time()
                func(file_contents, query)
                end_time = time.time()
                results[name] = end_time - start_time

            # Write the results to a CSV file
            with open("benchmark_results.csv", "w", newline="") as csvfile:
                fieldnames = ["Algorithm", "Execution Time (seconds)"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for name, time_taken in results.items():
                    writer.writerow(
                        {"Algorithm": name, "Execution Time (seconds)": time_taken}
                    )

            return results
    except FileNotFoundError:
        print("File not found. Please provide a valid file path.")


if __name__ == "__main__":
    path = "200k.txt"
    query = "10;0;1;26;0;9;3;0;"
    outcome = benchmark_algorithms(path, query)
    for name, duration in outcome.items():
        print(f"{name} took {duration:.6f} seconds to execute")
