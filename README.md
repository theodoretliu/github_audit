# Github Code Audit

## Installation

**Requires Docker to be installed**

```
docker build . -t audit:latest
```

## Usage

In the locally downloaded git repository of your choosing, run

```
docker run -p 8000:8000 -v ./:/code -it audit
```

Open `http://localhost:8000` to see the scrollable HTML of all the tracked git code in the directory. You can use `http://localhost:8000/directory_name` to see only a certain directory. **Note: only single-level directories are supported, e.g. http://localhost:8000/directory_name/sub/ will not work**
