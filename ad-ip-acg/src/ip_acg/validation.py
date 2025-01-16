def sanitize_rules():

    # dedup: set()
    # remove_whitespace: replace(" ", "")
    # remove_linebreaks: replace("\n", "")

    # populated?

    # split base ip and prefix:
    # fwd_slash = rule.find("/")
    # if fwd_slash != -1:
    #         address = self.input_rule[:fwd_slash]
    #         prefix = int(self.input_rule[fwd_slash+1:])
    #         return address, prefix
    #     else:
    #         return self.input_rule, DEFAULT_PREFIX

    # ipv4 match?
    # Ref regex pattern: https://stackoverflow.com/questions/5284147/validating-ipv4-
    #     addresses-with-regexp?page=1&tab=scoredesc#tab-top
    # pattern = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$"
    #     address = self.split()[0]

    #     if re.match(pattern, address):
    #         return True

    # ip address not in invalid range
    # ip_address, _ = split()

    # prefix allowed
    #  _, ip_prefix = self.split()
    #     if ip_prefix >= IP_ADDRESS_PREFIX_MIN:
    #         return True
    
    # -> rule_cleansed = Rule()

    target_rule = {
        "ipRule": "key",
        "ruleDesc": "value__desc_from_rule_in_yaml"
    }

    target_rules = "blablab"

    target_rules_sorted = sorted(
        target_rules,
        key=lambda target_rules: target_rules["ipRule"]
    )

    # validate if any content in target_rules
    # validate if not larger than max number of IP rules
    pass


def sanitize_ip_acg():

    # not longer than name length?
    # not longer than description length?
    pass


def integrate():
    pass
    

def sanitize_work_instruction():
    # WorkInstructionRaw to WorkInstruction
    # -> work_instruction = WorkInstruction()
    #   -> ip_acg_raw = IP_ACG()
    #   -> directory_raw = Directory()

    # logger.debug("Sanitized work_instruction:")

    # TODO: sanitize prefix > 32 or < 0
    pass
