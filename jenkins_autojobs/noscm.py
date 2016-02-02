#!/usr/bin/env python
# encoding: utf-8

'''
Automatically create jenkins jobs for the refs in a git repository.
Documentation: http://gvalkov.github.com/jenkins-autojobs/
'''

from __future__ import absolute_import

import os
import re
import sys
import lxml.etree

from . import job, main, utils


#------------------------------------------------------------------------------
def list_branches(config):
    # Noscm has no branch so this function could appear useless
    # But branches are very important in main.py
    # So we return at least one, even a dummy one.
    # It won't be used anyway
    cmd = ('echo', config['template'])
    out = utils.check_output(cmd, cwd='.').split(os.linesep)

    return (ref for ref in [i for i in out if i])



def create_job(ref, template, config, ref_config):
    '''Create a jenkins job.

       :param ref:         git ref name (ex: refs/heads/something)
       :param template:    the config of the template job to use
       :param config:      global config (parsed yaml)
       :param ref_config:  the effective config for this ref
       :returns:           the name of the newly created job
    '''

    match = ref_config['re'].match(ref)
    groups, groupdict = match.groups(), match.groupdict()

    # Placeholders available to the 'substitute' and 'namefmt' options.
    fmtdict = {}

    job_name = ref_config['namefmt'].format(*groups, **utils.merge(groupdict, fmtdict))
    job_obj  = job.Job(job_name, ref, template, main.jenkins)

    fmtdict['job_name'] = job_name

    print('. job name: %s' % job_obj.name)
    print('. job exists: %s' % job_obj.exists)

    # Set the state of the newly created job.
    job_obj.set_state(ref_config['enable'])

    # Since some plugins (such as sidebar links) can't interpolate the
    # job name, we do it for them.
    job_obj.substitute(list(ref_config['substitute'].items()), fmtdict, groups, groupdict)

    job_obj.create(
        overwrite=ref_config['overwrite'],
        build_on_create=ref_config['build-on-create'],
        dryrun=config['dryrun'],
        tag=ref_config['tag'],
        tag_method=config['tag-method']
    )

    if config['debug']:
        main.debug_refconfig(ref_config)

    return job_name

def _main(argv=sys.argv, config=None):
    main.main(argv[1:], config=config, create_job=create_job, list_branches=list_branches)

if __name__ == '__main__':
    _main()
