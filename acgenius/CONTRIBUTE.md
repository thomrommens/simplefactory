# Contribute

The following avenues are worth considering.

### Differentiate IP ACG sets
- Currently: all directories specified/retrieved, get the same set of IP ACGs applied.
- Change: Apply different sets of IP ACGs to different directories. 
- Effect: some directories get this IP ACG, other directories can get that IP ACG.
    
### Paginate
- Currently: no pagination for `boto3` calls is implemented.
- Change: add a paginator for managing IP ACGs at scale.
- Effect: ability to manage many IP ACGs.

### Update tags of IP ACG at update of rules
- Currently: AWS does not support updating tags of an existing IP ACG. 
- Change: if that would become available, we could add a tag `RulesLastModifiedInAWS` 
to the IP ACG, stating the last update of the IP ACG rules.
