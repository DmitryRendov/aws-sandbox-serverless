"""CRUD web app with Flask and DynamoDB."""

from decimal import Decimal
from os import environ
from time import ctime, time
from uuid import uuid1

from boto3 import resource, session
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# pylint: disable=unused-import
from flask import (  # noqa: F401,
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_s3 import FlaskS3


app = Flask(__name__)
# s3 options
# app.config["FLASKS3_BUCKET_NAME"] = "cloudology.by"
# s3 = FlaskS3(app)
# dynamodb config
ddb_client = resource("dynamodb")
if environ.get("IS_OFFLINE"):
    dev = session.Session(profile_name="sts", region_name="localhost")
    ddb_client = dev.resource("dynamodb", endpoint_url="http://localhost:8000")

TESTS_TABLE = ddb_client.Table(environ.get("TESTS_TABLE"))


@app.template_filter("ctime")
def epoch_to_ctime(epoch):
    """Jinja time filter that converts epoch to ctime.

    Args:
        epoch (float): Unix timestamp (1642981387.0677857)

    Returns:
        ctime (str): Converted epoch to the human-readable format ('Mon Jan 24 02:38:15 2022')

    """
    return ctime(epoch)


@app.route("/")
@app.route("/home")
def index():
    """Main page.

    Returns:
        Rendered `index` page content

    Urls:
        http://localhost:5000/
        http://localhost:5000/home

    """
    return render_template("index.html")


@app.route("/about")
def about():
    """About page.

    Returns:
        Rendered `about` page content

    Urls:
        http://localhost:5000/about

    """
    return render_template("about.html")


@app.route("/create-test", methods=["POST", "GET"])
def create_test():
    "CREATE new test based on input data from the form and render the page."
    if request.method == "POST":
        try:
            TESTS_TABLE.put_item(
                Item={
                    "id": str(uuid1()),
                    "date": Decimal(time()),
                    "title": request.form["title"],
                    "intro": request.form["intro"],
                    "text": request.form["text"],
                }
            )
            return redirect("/tests")
        except ClientError as err:
            if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
                print(err.response["Error"]["Message"])
    else:
        return render_template("create-test.html")
    return 1


@app.route("/tests")
def get_tests():
    "GET all tests from the table sorted by date in descending order."
    tests = TESTS_TABLE.scan()["Items"]
    tests.sort(key=lambda value: value["date"], reverse=True)
    return render_template("tests.html", tests=tests)


@app.route("/tests/<string:test_id>")
def get_test_details(test_id):
    "GET test details by test id."
    test = TESTS_TABLE.query(KeyConditionExpression=Key("id").eq(test_id))["Items"][0]
    return render_template("test_details.html", test=test)


@app.route("/tests/<string:test_id>/update", methods=["POST", "GET"])
def update_test(test_id):
    "UPDATE test data."
    test = TESTS_TABLE.query(KeyConditionExpression=Key("id").eq(test_id))["Items"][0]
    if request.method == "POST":
        try:
            ddb_client.Table("tests-table-dev").update_item(
                Key={"id": test["id"], "date": test["date"]},
                UpdateExpression="set title=:title, intro=:intro, #txt=:text",
                ExpressionAttributeNames={"#txt": "text"},
                ExpressionAttributeValues={
                    ":title": request.form["title"],
                    ":intro": request.form["intro"],
                    ":text": request.form["text"],
                },
                ReturnValues="UPDATED_NEW",
            )
            return redirect("/tests")
        except ClientError as err:
            if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
                print(err.response["Error"]["Message"])
    else:
        return render_template("test_update.html", test=test)
    return 1


@app.route("/tests/<string:test_id>/delete")
def delete_test(test_id):
    "DELETE test by test id."
    test = TESTS_TABLE.query(KeyConditionExpression=Key("id").eq(test_id))["Items"][0]
    try:
        TESTS_TABLE.delete_item(Key={"id": test["id"], "date": test["date"]})
    except ClientError as err:
        if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print(err.response["Error"]["Message"])
        else:
            raise
    else:
        return redirect("/tests")
    return 1


if __name__ == "__main__":
    app.run(debug=True)
