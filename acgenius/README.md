# `acgenius`

Simple overview of use/purpose.

## Description

An in-depth paragraph about your project and overview of use.

## Getting Started

### Dependencies

* Describe any prerequisites, libraries, OS version, etc., needed before installing program.
* ex. Windows 10

### Usage

Warnings:
- overwrite
- delete:
    - in general
    - interval between creating old and new; preferably create new IP ACG first and delete old IP ACG afterward.

settings.yaml validated in all routes, so keep it tidy

delete action separately to
- keep delete separated from create/update, otherwise confusing
- no accidental deletes

`{YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src>python -m acgenius create --dryrun`
`{YOUR_PROJECT_FOLDER}\simplefactory\acgenius\src>pytest \tests`

```
python -m acgenius status 
python -m acgenius create 
python -m acgenius update 
python -m acgenius delete 1234567890 1234567891

python -m acgenius create --dryrun
python -m acgenius update --dryrun --debug
python -m acgenius delete wsipg-1234567 wsipg-1234567891 --debug --dryrun 
```

## Documentation reference
Substack blog: [simplefactory.substack.com](https://simplefactory.substack.com)
(specify blog)


## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Thom Rommens, [Simplefactory](https://simplefactory.substack.com)


## Misc add
directory = always WorkSpace directory here; explain technically

IP Access Control Groups per Directory: You can associate up to 25 IP access control groups with a single directory
IP Access Control Groups per Region: You can create up to 100 IP access control groups per AWS region
-> as we just add all IP ACGs to each directory, the only validation we need is that the number of IP ACGs per directory does not exceed the maximum number of IP ACGs per directory allowed.


- generic

    - keep settings yaml close to actuality

- create

    - from scratch, create new IP ACG
        - just add IP ACGs in settings.yaml

    - with keeping current IP ACG in place, add new IP ACG
        - just add IP ACGs in settings.yaml (underneath existing)

- update

    - make sure the settings.yaml is in sync with your AWS target. In other words,
    IP ACGs specified in settings.yaml should be present in AWS, for an update to succeed.
    If they do not exist yet, run a `create` action first
    - update rules of existing IP ACGs
        - update rules in the settings.yaml

- delete
    
    - all IP ACGs
        - specify all in delete action
        - remove them from settings.yaml

    - some IP ACGs
        - specify some in delete action
        - remove applicable ones from settings.yaml


run tests
`pytest {YOUR_PROJECT_FOLDER}\simplefactory\acgenius\tests`


ruff check
ruff check {specify folder / file}