import re
transformations = {
        '@everyone': '@\u200beveryone',
        '@here': '@\u200bhere'
    }

pattern = re.compile('|'.join(transformations.keys()))


def clean_mention(content):

    def repl2(obj):
        return transformations.get(obj.group(0), '')

    return pattern.sub(repl2, str(content))
