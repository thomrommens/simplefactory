class DirectoryNoneFoundException(Exception):
    pass


class RuleLinebreakException(Exception):
    pass


class RuleIPV4FormatInvalidException(Exception):
    pass


class RulePrefixInvalidException(Exception):
    pass


class IPACGDuplicateRulesException(Exception):
    pass


class IPACGAmtRulesException(Exception):
    pass


class IPACGNameLengthException(Exception):
    pass


class IPACGDescriptionLengthException(Exception):
    pass


class IPACGNoneFoundException(Exception):
    pass


class UnexpectedException(Exception):
    pass
