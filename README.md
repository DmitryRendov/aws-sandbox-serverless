# aws-sandbox-serverless
Serverless solution for AWS Sandbox

## Install (CentOS 8)
```
sudo dnf install nodejs
sudo npm i serverless -g
```

## Configure (AWS)
Make sure, that you have an AWS profile configured in ~/.aws/config
```
[profile production-dmitry_rendov]
role_arn = arn:aws:iam::562495469185:role/dmitry_rendov
region = us-east-1
source_profile = sts
```
And you have valid STS session (aws-login.sh login)
Then configure ENV variables (or update .bash_rc) to enable AWS Profiles with Severless, including IAM cross-account role assumption.

```
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE="production-dmitry_rendov"
```
This enables any tool which uses the AWS SDK for Go (e.g. Serverless framework) to use AWS Profiles.

## Package and Deploy
You can just package the Lambda Functions, using the command
```
sls package
```
The resulted zip archives will be available in the folder .serverless

Or, you can deploy all the functions and resources, using the command
```
sls deploy
```

## Test locally ##

### Prerequisites

Install and configure [miniconda](https://docs.conda.io/en/latest/miniconda.html) on your local machine.
> Note: can be downloaded via `make setup` run.

Install the `dev` dependencies and activate `conda` environment with the following command:

```sh
make environment
conda activate aws-sandbox-serverless
```

### Development
Now you can start `AWS λ`, `API Gateway` and `DynamoDB` local with the following command:
```sh
sls offline start --stage dev
```
At this point, you can run web application locally with the following command:
```sh
sls wsgi serve --stage dev
```
Check that web application is up-and-running by the following link: http://localhost:5000/
