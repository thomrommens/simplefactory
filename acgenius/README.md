# `acgenius`

ACGenius is a Python command line utility to take control over access 
to Amazon Workspaces.

## Description

ACGenius is a simple utility to manage who (that is, which source IP addresses) 
can access Amazon WorkSpaces. It helps you to manage an extra layer of security. 
It facilitates governance of IP Access Control Groups (IP ACGs) rules, 
on who may use your virtual desktop infrastructure in AWS. 

Read all in detail on [https://simplefactory.substack.com](https://simplefactory.substack.com).

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
            - basics like DNS and subnets are already sorted in the default VPC.
    - AWS DirectoryService directory    
        - of any type (Simple AD is easiest)
        - registered in AWS WorkSpace, as a WorkSpaces directory
        - in active state
     - (optional) Amazon WorkSpace (Personal) to validate the actual effect of the IP ACG.

- Your environment for running ACGenius
    - Access keys stored to assume the IAM role
        - desktop: .aws file
        - pipeline: secretly stored variable / externally retrieved

    - Python 3.11 runtime
    - Other dependencies, as specified in Poetry.

## Set up your environment

- run `poetry install`
- activate the `venv` in your environment

## Usage

- Specify `settings.yaml`
    - `settings.yaml` is the heart of this utility.
    - it is validated in all routes to keep source ('work instruction') in the repo, 
    and target ('inventory') in AWS, in sync.

- Run 
`{YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src>python -m acgenius {action} --dryrun --debug`
    - {action} can be any of `status`, `create`, `update`, `delete`.
        - `status`: see what's the current state of IP ACGs in your directory in AWS.
        - `create`: create new IP ACG(s)
        - `update`: replace current rules in the IP ACG, with new ones.
            - the utility will first validate if it can match IP ACGs 
            from `settings.yaml` with the target in AWS. 
            - if so, it overwrites the full set of existing rules. 
            Old rules will not be preserved.
        - `delete`: delete current IP ACG(s)
            - separated from `status`, `create`, and `update`.
            - does not use `settings.yaml` for input, to avoid confusing 
            and to prevent accidental deletes. 
            - just pass the IP ACG ids as space-separated strings, e.g., 
                - `python -m acgenius delete wsipg-123456789 wsipg-987654321`
            - think about not to delete your current IP ACG
            before you have a new one applied, to keep your AWS directory secure.
            
    - options can be applied at all actions:
        - `--dryrun`: just see what `create`, `update`, `delete` would do;
        with the option enabled, ACGenius will not execute the action
        - `--debug`: get more detail in logs.        


## Develop

- Create a feature branch from main.
- Develop.

## Test

- Run `pytest` generally, or specifically per sub folder / file:
    - `{YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src>pytest\tests`
    - `{YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src>pytest\tests\acgenius\resources`
    - `{YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src>pytest\tests\acgenius\resources\directories\test_inventory_directories.py`

- Run `ruff` to inspect or to change (Black included), likewise:
    - `ruff check {YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src\acgenius\resources`
    - `ruff format {YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src\acgenius\resources`


## Authors

Thom Rommens, [Simplefactory](https://simplefactory.substack.com)
