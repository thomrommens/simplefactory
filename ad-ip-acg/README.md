# Project Title

Simple overview of use/purpose.

## Description

An in-depth paragraph about your project and overview of use.

## Getting Started

### Dependencies

* Describe any prerequisites, libraries, OS version, etc., needed before installing program.
* ex. Windows 10

### Usage

* update overwrite existing IP ACGs
```
code blocks for commands
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


#   - if you *create* IP ACGs, you don't know the 'id' yet.
#     Leave "placeholder" as is.
#   - if you update existing IP ACGs, technically the existing IP ACG
#     will be disassciated from the directory, and deleted, before
#     a new IP ACG will be created.
# -> at update possible to keep, right?

# dry run for validating settings.yaml


IP Access Control Groups per Directory: You can associate up to 25 IP access control groups with a single directory

IP Access Control Groups per Region: You can create up to 100 IP access control groups per AWS region


python script_name.py --delete-list d-1234567890 d-0987654321 d-1122334455

delete-list, to
- keep delete separated from create/update, otherwise confusing
- no accidental deletes
- 


use cases

- generic

    - keep settings yaml close to actuality

- create

    - from scratch, create new IP ACG
        - just add IP ACGs in settings.yaml

    - with keeping current IP ACG in place, add new IP ACG
        - just add IP ACGs in settings.yaml (underneath existing)

- update

    - update rules of existing IP ACGs
        - update rules in the settings.yaml

- delete
    
    - all IP ACGs
        - specify all in delete action
        - remove them from settings.yaml

    - some IP ACGs
        - specify some in delete action
        - remove applicable ones from settings.yaml

<!-- # - python -m main create
# - python -m main update 
# - python -m main delete 1234567890, 1234567891
# - python -m main action --debug 
# - python -m main action --dryrun -->