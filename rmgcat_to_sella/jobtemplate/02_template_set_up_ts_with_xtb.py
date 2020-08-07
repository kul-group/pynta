#!/usr/bin/env python3

import sys
import os
from glob import glob
from pathlib import Path

from rmgcat_to_sella.ts import TS

from balsam.launcher.dag import BalsamJob, add_dependency
from balsam.core.models import ApplicationDefinition

slab = '{slab}'
repeats = {repeats}
yamlfile = '{yamlfile}'
facetpath = '{facetpath}'
rotAngle = {rotAngle}
scfactor = {scfactor}
scfactor_surface = {scfactor_surface}
pytemplate_xtb = '{pytemplate_xtb}'
species = {species_list}
current_dir = os.path.dirname(os.getcwd())
minima_dir = os.path.join(facetpath, 'minima')
scaled1 = {scaled1}
scaled2 = {scaled2}
ts_dir = 'TS_estimate'
workflow_name = yamlfile+facetpath+'02'
dependency_workflow_name = yamlfile+facetpath+'01'
creation_dir = '{creation_dir}'

ts = TS(facetpath, slab, ts_dir, yamlfile, repeats, creation_dir)
ts.copy_minimas_prev_calculated(current_dir, species, minima_dir)
ts.prepare_ts_estimate(scfactor, scfactor_surface, rotAngle,
                       pytemplate_xtb, species, scaled1, scaled2)

myPython, created = ApplicationDefinition.objects.get_or_create(
    name="Python",
    executable=sys.executable
)
myPython.save()
pending_simulations = BalsamJob.objects.filter(
    workflow__contains=dependency_workflow_name
).exclude(state="JOB_FINISHED")
cwd = Path.cwd().as_posix()
for py_script in glob('{facetpath}/TS_estimate/*/*.py'):
    job_dir = Path.cwd().as_posix() + '/' + '/'.join(
        py_script.strip().split('/')[:-1]
    )
    script_name = py_script.strip().split('/')[-1]
    job_to_add = BalsamJob(
            name=script_name,
            workflow=workflow_name,
            application=myPython.name,
            args=cwd + '/' + py_script,
            input_files='',
            ranks_per_node=1,
            node_packing_count=64,
            user_workdir=job_dir,
            )
    job_to_add.save()
    for job in pending_simulations:
        add_dependency(job, job_to_add)  # parent, child
