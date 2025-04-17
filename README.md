# Maria Dashboard


## 1. Requirements

- Python (3.13.0)
- Docker
- Make
- [uv](https://pypi.org/project/uv/)

## 2. How to run

1. Install dependencies

    ```bash
    make install
    ```

2. Run

    Locally
    ```bash
    make run
    ```
    Docker
    ```bash
    make compose
    make seed # add dev database dump
    ```
