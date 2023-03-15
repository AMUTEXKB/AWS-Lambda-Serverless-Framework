#!/bin/bash

STAGE=dev

(cd layers && serverless plugin install -n serverless-deployment-bucket --stage $STAGE)
(cd components/community && serverless plugin install -n serverless-deployment-bucket --stage $STAGE && serverless plugin install -n serverless-latest-layer-version --stage $STAGE && serverless plugin install -n serverless-ssm-fetch --stage $STAGE)
(cd components/application_tracker && serverless plugin install -n serverless-deployment-bucket --stage $STAGE && serverless plugin install -n serverless-latest-layer-version --stage $STAGE)
(cd components/job_applications && serverless plugin install -n serverless-deployment-bucket --stage $STAGE && serverless plugin install -n serverless-latest-layer-version --stage $STAGE)
(sls deploy --stage $STAGE --verbose)