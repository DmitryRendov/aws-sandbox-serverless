"Sample of lambda function."

import json


def hello(event, context):  # pylint: disable=unused-argument
    """Hello lambda function.

    Args:
        event    (dict): Contains information from the invoking service
                         (service defines the event structure)

        context   (obj): Contains methods and properties that provide information
                         about the invocation, function, and runtime environmenti.
                         (function name, version, memory limits, request id and etc.)

    Returns:
        response (dict): Contains request response from the handler
                         (200 status code and event data)

    """
    body = {
        "message": "Go Serverless v2.0! Your function executed successfully!",
        "input": event,
    }
    response = {"statusCode": 200, "body": json.dumps(body)}
    return response
