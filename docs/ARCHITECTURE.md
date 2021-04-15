# Taskflow architecture

Taskflow consists of 2 components: the CLI application `taskflow`, and the daemon `taskflowd`.

`taskflowd` typically runs as a single background process, that monitors the system's resources, schedules tasks, and provides a RESTful API over HTTP. The `taskflow` CLI communicates with `taskflowd` according to user input.

`taskflowd` is a single-thread process that makes use of Python's async capabilities, using the `uvloop` library. It runs 3 looping coroutines: the system monitor loop, the scheduler loop, and the server loop. The system monitor loop continually updates data on available resources in the system. The scheduler loop reads the current system state and the list of pending jobs to decide if any job should start. Lastly, the server loop runs a `FastAPI` app, serving incoming requests.

When a task is scheduled with `taskflow run`, the CLI establishes a WebSocket connection with the daemon. It waits for the start signal from the daemon, then starts the requested process in the current shell. The connection is kept alive for the duration of the process.
