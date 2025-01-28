status
✅ plain
✅ dryrun
✅ debug
✅ dryrun debug
✅ debug dryrun

create
✅ plain
✅ dryrun
✅ debug
✅ dryrun debug
✅ debug dryrun
✅ create from scratch
✅ create again exact same
✅ create additional IP ACGs next to existing
- too many rules
- no rules
- no IP ACG desc

update
✅ plain
✅ dryrun
✅ debug
✅ dryrun debug
✅ debug dryrun
- too many rules
- no tag value
- int instead of string value
- try to update rules of non-existent ip acg

delete
✅ plain
✅ dryrun
✅ debug
✅dryrun debug
✅ debug dryrun

✅specify invalid ids for deletion in cli
✅one IP ACG could be deleted, other not (other not recognized)

SETTINGS
- only key
- only value
- none

GENERAL
- all combinations with --debug, --dryrun


- no directory specified
- only directory id specified
- unacceptable prefix
- per validation specified