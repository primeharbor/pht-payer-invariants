# Copyright 2024 Chris Farris <chris@primeharbor.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

AWS_ACCOUNT := $(shell aws sts get-caller-identity --query Account --output text)
ADMIN_ROLE ?= AWSReservedSSO_AdministratorAccess
VARFILE ?= vars.txt
STACK_NAME ?= InvariantEnforcerStack
PERM_BOUNDARY_NAME ?= PayerPermissionsBoundary

create-boundary:
	./create_pb_file.py $(VARFILE) pb_policy.json
	aws iam create-policy --policy-name PayerPermissionsBoundary --description "Permission Boundary for Payer Account" --policy-document file://pb_policy.json

delete-boundary:
	aws iam delete-policy --policy-arn arn:aws:iam::$(AWS_ACCOUNT):policy/$(PERM_BOUNDARY_NAME)

update-boundary:
	./create_pb_file.py $(VARFILE) pb_policy.json
	aws iam create-policy-version --policy-arn arn:aws:iam::$(AWS_ACCOUNT):policy/$(PERM_BOUNDARY_NAME) --policy-document file://pb_policy.json --set-as-default

test-attachment:
	 ./attach_permission_boundary.py arn:aws:iam::$(AWS_ACCOUNT):policy/$(PERM_BOUNDARY_NAME) --dry-run

force-attachment:
	 ./attach_permission_boundary.py arn:aws:iam::$(AWS_ACCOUNT):policy/$(PERM_BOUNDARY_NAME)

create-enforcer:
	aws cloudformation create-stack \
		--stack-name $(STACK_NAME) \
		--capabilities CAPABILITY_NAMED_IAM \
		--template-body file://cloudformation/InvariantEnforcer-Template.yaml \
		--parameters ParameterKey=PermissionBoundaryName,ParameterValue=$(PERM_BOUNDARY_NAME)\
					 ParameterKey=AdminRoleName,ParameterValue=$(ADMIN_ROLE)

update-enforcer:
	aws cloudformation update-stack \
		--stack-name $(STACK_NAME) \
		--capabilities CAPABILITY_NAMED_IAM \
		--template-body file://cloudformation/InvariantEnforcer-Template.yaml \
		--parameters ParameterKey=PermissionBoundaryName,ParameterValue=$(PERM_BOUNDARY_NAME) \
					 ParameterKey=AdminRoleName,ParameterValue=$(ADMIN_ROLE)

