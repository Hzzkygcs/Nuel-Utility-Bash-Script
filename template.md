Add Owner tag to {service_name}

## Summary

- Add AWS `Owner` tag. (see: [LOC2-873](https://29022131.atlassian.net/browse/LOC2-873))

These changes add `Owner` tag to *at least* one of these AWS services:
- ECS
- Cloudwatch
- ALB
- DynamoDB
- SQS
- Opensearch / Elasticsearch


This is done to allow us to categorize which service belongs to which team (`UNS` or `LOC`).
By categorizing each service to its own team, we can monitor the AWS services more easily.
For example, if we want to know which team causes the most expensive monthly price, this Owner tag will be helpful.

I appreciate all kinds of feedback, be it syntax/semantic correctness, best practices, etc., so please feel free to give me any suggestions.

<!-- 
## Dependency

- This PR depends on {referenced_pr}
So, that PR needs to be merged and be released in its own version. Only then this PR can be merged and applied.
-->


## Test Plan
```
{user_input}
```

## Subscribers
<!-- mentions who should be notified about your changes, e.g.:

- @username
- @organization/team-name

These people will get GitHub notifications after this PR is created
-->