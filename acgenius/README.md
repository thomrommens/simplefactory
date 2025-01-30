# `acgenius`

ACGenius is a Python command line utility to take control over external access 
to Amazon Workspaces.

## Description

ACGenius is a simple utility to manage who (that is, which source IP addresses) 
can access an Amazon WorkSpace. It helps you to manage an extra layer of security. 
It facilitates governance of IP Access Control Groups (IP ACGs) rules 
on who may use your virtual desktop infrastructure in AWS. 

Read all in detail: [substack link]

## Prerequisites

- AWS
    - account
    - IAM role with permissions: 
        - `workspaces:AssociateIpGroups`
        - `workspaces:AuthorizeIpRules`
        - `workspaces:CreateIpGroup`
        - `workspaces:CreateTags`
        - `workspaces:DeleteIpGroup`
        - `workspaces:DescribeIpGroups`
        - `workspaces:DescribeWorkspaceDirectories`
        - `workspaces:DisassociateIpGroups`
        - `workspaces:RevokeIpRules`
        - `workspaces:UpdateRulesOfIpGroup`
    - VPC with at least 2 subnets
        - the default VPC will do
            - basics like DNS and subnets are already sorted
    - AWS DirectoryService directory    
        - of any type (Simple AD is easiest)
        - registered in AWS WorkSpace, as a WorkSpaces directory
        - in Active state
     - (optional) Amazon WorkSpace (Personal) to validate the actual effect of the IP ACG

- Your environment running ACGenius
    - Access keys stored to assume the IAM role
        - desktop: .aws file
        - pipeline: secretly stored

## Setting your environment

- run `poetry install`
- activate the `venv` in your environment

## Usage

- Specify settings.yaml
    - settings.yaml is the heart of this utility.
    - it is validated in all routes to keep source ('work instruction') in the repo, 
    and target ('inventory') in AWS, in sync.

- Run 
`{YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src>python -m acgenius {action} --dryrun --debug`
    - {action} can be any of `status`, `create`, `update`, `delete`.
        - `status`
        - `update`:
            - will first see if it can match IP ACGs from settings.yaml 
            with the target in AWS. 
            - overwrites the full set of existing rules. Old rules will not be stored.
        - `delete`: 
            - separated from `status`, `create`, and `update`.
            - does not use settings.yaml for input, to avoid confusing 
            and to prevent accidental deletes. 
            - just pass the IP ACG ids as space-separated strings. 
            - think about not to delete your current IP ACG
            before you have a new one applied, to keep your AWS directory secure.
            `python -m acgenius delete wsipg-123456789 wsipg-987654321
    
    - options can be applied at all actions:
        - `--dryrun`: just see what `create`, `update`, `delete` would do, 
        does not take actual action) 
        - `--debug`: more detail in logs.        


## Develop

- Create a feature branch from main.
- Develop.

## Test

- Run `pytest` generally, or specifically per sub folder / file:
`{YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src>pytest\tests`
`{YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src>pytest\tests\acgenius\resources`
`{YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src>pytest\tests\acgenius\resources\directories\test_inventory_directories.py`

- Run `ruff` to inspect or to change (Black included), likewise:
`ruff check {YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src\acgenius\resources`
`ruff format {YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src\acgenius\resources`


## Authors

Thom Rommens, [Simplefactory](https://simplefactory.substack.com)
