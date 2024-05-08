# LambdaQ

**LambdaQ** ("lambda queue") is a Python package that helps you to write Amazon Web Services Lambda functions that receive events from Step Functions state machines via SQS queues.

## Why use it?

Frankly, I write a lot of Lambda functions that need to be invoked by Step Functions state machines via SQS queues, and my team is as bored reviewing the boilerplate as I am writing it.

I also find myself needing to upgrade Lambda functions from direct invocation to indirect via-SQS invocation for resilience, and I wanted a handler that supports both event styles during migrations.

So, LambdaQ helps you to write clean, testable Lambda functions without needing to care whether the event arrived directly or via a queue.

## Example

Say you want to build a Lambda function that sums two numbers together then returns the result. You want this function to be invoked by a Step Functions state machine, and you want the function to be deployed behind an SQS queue for resilience.

With LambdaQ, your script looks like this:

```python
from typing import Any, TypedDict
from lambdaq import Metadata, handle_event

class Inputs(TypedDict):
    x: int
    y: int
    task_token: str

class Sum(TypedDict):
    result: int

def main(event: Any, context: Any) -> Sum | None:
    return handle_event(
        event,
        perform_sum,
        task_token_key="task_token",
    )

def perform_sum(inputs: Inputs, metadata: Metadata) -> Sum:
    return Sum(result=inputs["x"] + inputs["y"])
```

The `lambdaq.handle_event` function reads the invocation event, a reference to a message handler, and the key of the task token injected by the state machine.

If the task token key is omitted then the work will still be performed, but the state won't be reported back to Step Functions. This would be used, for example, for functions invoked by SQS queues that don't need to report back any status.

The message handler--`perform_sum` in this example--reads a strongly-typed message and returns a strongly-typed response.

## How does it work?

Behind the scenes, LambdaQ checks if the event describes a single direct invocation or a collection of (one or more) messages plucked from an SQS queue.

If the event describes a single direct invocation, LambdaQ calls the message handler then returns the response directly.

if the event describes a collection of messages from a queue then LambdaQ calls the message handler for each message, and includes calls to the Step Functions `send_task_success`and `send_task_failure` APIs as-and-when each message succeeds or fails.

## Installation

LambdaQ requires Python 3.10 or later and can be installed from [PyPI](https://pypi.org/project/lambdaq/).

```shell
pip install lambdaq
```

## Support

Please submit all your questions, feature requests and bug reports at [github.com/cariad/lambdaq/issues](https://github.com/cariad/lambdaq/issues). Thank you!

## Licence

LambdaQ is [open-source](https://github.com/cariad/lambdaq) and released under the [MIT License](https://github.com/cariad/lambdaq/blob/main/LICENSE).

You don't have to give attribution in your project, but--as a freelance developer with rent to pay--I appreciate it!

## Author

Hello! 👋 I'm **Cariad Eccleston**, and I'm a freelance Amazon Web Services architect, DevOps evangelist, CI/CD pipeline engineer and backend developer.

You can find me at [cariad.earth](https://cariad.earth), [github.com/cariad](https://github.com/cariad), [linkedin.com/in/cariad](https://linkedin.com/in/cariad) and on the Fediverse at [@cariad@gamedev.lgbt](https://gamedev.lgbt/@cariad).
