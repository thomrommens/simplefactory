# TODO: consistently name exceptions

class DirectoryNoneFoundException(Exception):
    pass


class RuleLinebreakException(Exception):
    pass


class RuleIPV4FormatInvalidException(Exception):
    pass


class RulePrefixInvalidException(Exception):
    pass


class RuleDescriptionLengthException(Exception):
    pass


class IPACGNoneFoundException(Exception):
    pass


class IPACGDuplicateRulesException(Exception):
    pass


class IPACGAmtRulesException(Exception):
    pass


class IPACGNameDuplicateException(Exception):
    pass


class IPACGNameLengthException(Exception):
    pass


class IPACGDescriptionLengthException(Exception):
    pass


class IPACGCreateException(Exception):
    pass


class IPACGIdMatchException(Exception):
    pass


class IpAcgDisassociationException(Exception):
    pass


class IPACGNoneSpecifiedForDeleteException(Exception):
    pass


class UnexpectedException(Exception):
    pass
