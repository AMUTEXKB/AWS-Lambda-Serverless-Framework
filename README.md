# Serverless Framework -

## Overview
I've used Serverles Framework recommended structure for services. [REFERENCE](https://www.serverless.com/framework/docs/guides/compose)
Basically all the entities/services gets to have their own serverless.yaml files and loosely coupled together.
## Prequisites
- Serverless Framework 3.21.0
- AWS Credentials
- Python3.9

You can install the Serverless Framework from [here](https://www.serverless.com/framework/docs/install-standalone)

### Layers
If you checkout `serverless.yaml`, we've created one layer
1. auth: It'll contains all the plugins required for our authorizer

### Environment file
`.env.{STAGE}` file.
Make sure to update the files as per your requirements.

## How to run
I've created two scripts files to automatically handles the deployment and deleting of the stacks.
You can deploy the stack using the following command
```
    ./deploy.sh
```

You can delete the stack using the following command
```
    ./remove.sh
```
