# version_info should conform to PEP 386
# (major, minor, micro, alpha/beta/rc/final, #)
# (1, 1, 2, 'alpha', 0) => "1.1.2.dev"
# (1, 2, 0, 'beta', 2) => "1.2b2"
__version_info__ = (0, 1, 0, 'alpha', 0)


def _get_version():  # pragma: no cover
    " Returns a PEP 386-compliant version number from version_info. "
    assert len(__version_info__) == 5
    assert __version_info__[3] in ('alpha', 'beta', 'rc', 'final')

    parts = 2 if __version_info__[2] == 0 else 3
    main = '.'.join(map(str, __version_info__[:parts]))

    sub = ''
    if __version_info__[3] == 'alpha' and __version_info__[4] == 0:
        # TODO: maybe append some sort of git info here??
        sub = '.dev'
    elif __version_info__[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[__version_info__[3]] + str(__version_info__[4])

    return str(main + sub)

__version__ = _get_version()