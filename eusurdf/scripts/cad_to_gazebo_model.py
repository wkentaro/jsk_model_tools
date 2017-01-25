#!/usr/bin/env python

import os.path as osp
import os
import shutil
import shlex
import argparse
import subprocess


CONFIG_TEMPLATE = '''\
<?xml version="1.0"?>
<model>
  <name>{NAME}</name>
  <version>1.0</version>
  <sdf version="1.0">model.sdf</sdf>
  <description>A gazebo model of {NAME}</description>
</model>
'''

SDF_TEMPLATE = '''\
<?xml version="1.0" ?>
<sdf version="1.4">
  <model name="{NAME}">
    <link name="{NAME}_link">
      <inertial>
        <pose>0 0 0 0 0 0</pose>
        <mass>{MASS}</mass>
      </inertial>

      <visual name="{NAME}_visual">
        <pose>0 0 0 0 0 0</pose>
        <!--
        <material>
          <script>
            <uri>model://{NAME}/materials/scripts</uri>
            <uri>model://{NAME}/materials/textures</uri>
            <name>{NAME}</name>
          </script>
        </material>
        -->
        <geometry>
          <mesh>
            <uri>model://{NAME}/meshes/{NAME}.dae</uri>
          </mesh>
        </geometry>
      </visual>

      <collision name="{NAME}_collision">
        <pose>0 0 0 0 0 0</pose>
        <geometry>
          <mesh>
            <uri>model://{NAME}/meshes/{NAME}.dae</uri>
          </mesh>
        </geometry>
        <surface>
          <friction>
            <ode>
              <mu>{FRICTION_MU}</mu>
              <mu2>{FRICTION_MU2}</mu2>
            </ode>
          </friction>
        </surface>
      </collision>

    </link>
  </model>
</sdf>
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cad_model')
    parser.add_argument('--name')
    parser.add_argument('--out')
    parser.add_argument('--mass', type=float, default=0.08)
    parser.add_argument('--friction-mu', type=float, default=0.8)
    parser.add_argument('--friction-mu2', type=float, default=0.8)
    args = parser.parse_args()

    cad_model = args.cad_model
    name = args.name
    out_dir = args.out
    mass = args.mass
    friction_mu = args.friction_mu
    friction_mu2 = args.friction_mu2

    basename, ext = osp.splitext(osp.basename(cad_model))
    if name is None:
        name = basename

    if out_dir is None:
        out_dir = name
    if not osp.exists(out_dir):
        os.makedirs(out_dir)

    models_dir = osp.join(out_dir, 'meshes')
    if not osp.exists(models_dir):
        os.mkdir(models_dir)
    if ext == '.dae':
        shutil.copy(cad_model, osp.join(models_dir, osp.basename(cad_model)))
    else:
        cmd = 'meshlabserver -i {} -o {}'.format(cad_model, osp.join(models_dir, name + '.dae'))
        subprocess.call(shlex.split(cmd))

    sdf_file = osp.join(out_dir, 'model.sdf')
    sdf = SDF_TEMPLATE.format(
        NAME=name,
        CAD_MODEL=cad_model,
        MASS=mass,
        FRICTION_MU=friction_mu,
        FRICTION_MU2=friction_mu2,
    )
    with open(sdf_file, 'w') as f:
        f.write(sdf)

    config_file = osp.join(out_dir, 'model.config')
    config = CONFIG_TEMPLATE.format(NAME=name)
    with open(config_file, 'w') as f:
        f.write(config)


if __name__ == '__main__':
    main()
