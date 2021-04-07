<p align="center">
    <img
    src="images/taskflow.png"
    alt="logo"
    height="100px"/>
</p>

# Taskflow: Share system resources without breaking a sweat
Taskflow is a UNIX utility that allows users to schedule arbitrary tasks to run when the system has enough resources available.

- [Why Taskflow](#why-taskflow)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Contribution](#contribution)

## Why Taskflow?
Taskflow is best explained with an example. Let's say 3 users, Alice, Bob and Chuck are sharing the same workstation. They all need to run tasks that uses the workstation GPU (eg. training AI models). Alice runs her task first, which takes up the entire GPU memory. Now Bob and Chuck have to wait for Alice's task to finish before they can run theirs, checking the workstation every now and then to see if it's their turn. Taskflow can instead do the waiting for them by monitoring GPU usage and run their tasks when enough resources is available.

If you ever find yourself in Bob and Chuck's situation, Taskflow may be able to help you :)

## Installation
TODO

## Usage
### Basic usage
Once Taskflow is installed, schedule your tasks using `taskflow run`. Use CLI options to declare the amount of resources the task needs. Currently, RAM and GPU memory are supported resources.
```bash
# Run task using 5GB RAM
taskflow run -m 5G "my-command --option X Y"

# Run task using 10GB memory on GPU 0
taskflow run --gpu 0:10G "my-command --option X Y"
```

All environment settings in the shell (eg. virtualenv, conda, etc...) are preserved when using Taskflow. This means you can drop Taskflow in any existing project or workflow with zero changes.

### View current tasks
You can view tasks managed by Taskflow using `taskflow ps`

### Usage notes
Taskflow does not check whether a task actually uses the resources it asks for, meaning you can be give a rough estimate of how much resource a task need to not fail.

After starting a task, Taskflow has a default timeout of 60 seconds before another task can be scheduled. This is to make sure the previous task has locked up all needed resource before starting the next one. You can change this value using the `-d` option of `taskflow run`.

Refer to `taskflow --help` for detailed documentation of available commands.

## Architecture
If you're curious about how Taskflow works, refer to [this file](ARCHITECTURE.md).

## Contribution
To contribute to Taskflow development, refer to the [Contribution guide](CONTRIBUTING.md).
