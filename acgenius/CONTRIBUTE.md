- apply different set of IP ACGs to a different directory 
(now, all directories get the same IP ACGs applied).

- delete a specified set of IP ACGs
(now, all are deleted)

- add paginator - now smaller scale assumed 

- validate these settings.validation.ip_address.invalid themselves, for IPv4 format?

- AWS currently does not support updating tags of an existing IP ACG. If that would become available, we could add a tag "RulesLastModifiedInAWS" to the IP ACG.