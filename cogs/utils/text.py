import re


def clean_mention(content):
    transformations = {
        '@everyone': '@\u200beveryone',
        '@here': '@\u200bhere'
    }

    def repl2(obj):
        return transformations.get(obj.group(0), '')

    pattern = re.compile('|'.join(transformations.keys()))
    return pattern.sub(repl2, str(content))
