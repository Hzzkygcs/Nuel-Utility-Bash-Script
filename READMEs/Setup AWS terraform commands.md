# Configuring AWS CLI Access Through AWS SSO

## Introduction

The AWS Command Line Interface (CLI) is a unified tool to manage your AWS services. With just one tool to download and configure, you can control multiple AWS services from the command line and automate them through scripts.

## Prerequisites

- [awscli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) vesion 2.0.0 or later.

- Access to AWS SSO through [JumpCloud](https://console.jumpcloud.com/login#/).

- Log in to [https://tvlk.awsapps.com/start/](https://tvlk.awsapps.com/start/) to confirm access. 

- [Granted CLI](https://docs.commonfate.io/granted/getting-started): 

  ```
  #For MacOS
  brew tap common-fate/granted
  brew install granted

  #For Ubuntu
  curl -OL releases.commonfate.io/granted/v0.14.1/granted_0.14.1_linux_x86_64.tar.gz
  sudo tar -zxvf ./granted_0.14.1_linux_x86_64.tar.gz -C /usr/local/bin/
  ```

- [jq](https://jqlang.github.io/jq/):

  ```
  # For MacOS
  brew install jq #for macos

  # For Ubuntu
  sudo apt-get install jq #for ubuntu
  ```

## Steps

**1. Configure AWS SSO**

Backup your aws config file before running the sso populate command

```
cp ~/.aws/config ~/.aws/config.backup
```

> ⚠️ Ensure you've installed all the three prerequisites above before continuing.

**Execute the following command and click `Allow` when prompted afterwards:**
_(please do not edit this command, just run as it is)_

```
granted sso populate --sso-region ap-southeast-1 --profile-template "{{ .RoleName }}@{{ .AccountName }}" https://tvlk.awsapps.com/start/
```

**2. Configure Automatically Role Reassume**

If you use Zsh, execute the command below. For other shells, skip it.  

```
echo 'export GRANTED_ENABLE_AUTO_REASSUME=true' >> ~/.zshrc
```

> ℹ️ Note that at this point, AWS CLI will automatically rotate your IAM credential and you won't have to login again until your AWS SSO credential expires (around 8 hours). So you don’t need to re-login every hour like `aws-google-auth`.

**3. Assume a Role**

> ℹ️ To get a list of your roles, go to [https://tvlk.awsapps.com/start/]() and choose the respective AWS account.

```bash
assume RoleName@AccountAlias
terraform init
terraform apply
```

Example: 

```bash
assume SuperAdmin@tvlk-tsi-stg
terraform init
terraform apply
```

Or when using the AWS CLI, you can use the `--profile` flag:

```bash
aws s3 ls --profile SuperAdmin@tvlk-tsi-stg
```

## Next

[Configuring Console Access Through AWS SSO](../../console/configuring-aws-console-access-through-aws-sso/README.md).
