# Copyright 2017 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.


DEPS = [
  'checkout',
  'recipe_engine/file',
  'recipe_engine/path',
  'recipe_engine/properties',
  'run',
  'vars',
]


def RunSteps(api):
  api.vars.setup()

  bot_update = True
  if 'NoDEPS' in api.properties['buildername']:
    bot_update = False

  checkout_root = api.checkout.default_checkout_root
  checkout_chromium = False
  checkout_flutter = False
  extra_gclient_env = {}
  flutter_android = False
  parent_rev = False
  if 'CommandBuffer' in api.vars.builder_name:
    checkout_chromium = True
  if 'RecreateSKPs' in api.vars.builder_name:
    checkout_chromium = True
    extra_gclient_env['CPPFLAGS'] = (
        '-DSK_ALLOW_CROSSPROCESS_PICTUREIMAGEFILTERS=1')
  if 'Flutter' in api.vars.builder_name:
    checkout_root = checkout_root.join('flutter')
    checkout_flutter = True
    if 'Android' in api.vars.builder_name:
      flutter_android = True
  if 'ParentRevision' in api.vars.builder_name:
    parent_rev = True

  if bot_update:
    api.checkout.bot_update(
        checkout_root=checkout_root,
        checkout_chromium=checkout_chromium,
        checkout_flutter=checkout_flutter,
        extra_gclient_env=extra_gclient_env,
        flutter_android=flutter_android,
        parent_rev=parent_rev)
  else:
    api.checkout.git(checkout_root=api.path['start_dir'])
  api.file.ensure_directory('makedirs tmp_dir', api.vars.tmp_dir)


TEST_BUILDERS = [
  'Build-Win-Clang-x86_64-Release-ParentRevision',
  'Build-Mac-Clang-x86_64-Debug-CommandBuffer',
  'Housekeeper-Weekly-RecreateSKPs',
]


def GenTests(api):
  for buildername in TEST_BUILDERS:
    yield (
        api.test(buildername) +
        api.properties(buildername=buildername,
                       repository='https://skia.googlesource.com/skia.git',
                       revision='abc123',
                       path_config='kitchen',
                       swarm_out_dir='[SWARM_OUT_DIR]')
    )

  buildername = 'Build-Win-Clang-x86_64-Release-Vulkan'
  yield (
      api.test('test') +
      api.properties(buildername=buildername,
                     repository='https://skia.googlesource.com/skia.git',
                     revision='abc123',
                     path_config='kitchen',
                     swarm_out_dir='[SWARM_OUT_DIR]') +
      api.properties(patch_storage='gerrit') +
      api.properties.tryserver(
          buildername=buildername,
          gerrit_project='skia',
          gerrit_url='https://skia-review.googlesource.com/',
      )
    )

  buildername = 'Build-Win-Clang-x86_64-Release-ParentRevision'
  yield (
      api.test('parent_revision_trybot') +
      api.properties(buildername=buildername,
                     repository='https://skia.googlesource.com/skia.git',
                     revision='abc123',
                     path_config='kitchen',
                     swarm_out_dir='[SWARM_OUT_DIR]',
                     patch_issue=500,
                     patch_set=1,
                     patch_storage='gerrit') +
      api.properties.tryserver(
          buildername=buildername,
          gerrit_project='skia',
          gerrit_url='https://skia-review.googlesource.com/',
      )
  )

  buildername = 'Build-Debian9-GCC-x86_64-Release-Flutter_Android'
  yield (
      api.test('flutter_trybot') +
      api.properties(
          repository='https://skia.googlesource.com/skia.git',
          buildername=buildername,
          path_config='kitchen',
          swarm_out_dir='[SWARM_OUT_DIR]',
          revision='abc123',
          patch_issue=500,
          patch_set=1,
          patch_storage='gerrit') +
      api.properties.tryserver(
          buildername=buildername,
          gerrit_project='skia',
          gerrit_url='https://skia-review.googlesource.com/',
      ) +
      api.path.exists(
          api.path['start_dir'].join('tmp', 'uninteresting_hashes.txt')
      )
  )

  builder = 'Build-Debian9-Clang-x86_64-Release-NoDEPS'
  yield (
      api.test(builder) +
      api.properties(buildername=builder,
                     repository='https://skia.googlesource.com/skia.git',
                     revision='abc123',
                     path_config='kitchen',
                     swarm_out_dir='[SWARM_OUT_DIR]',
                     patch_issue=500,
                     patch_repo='https://skia.googlesource.com/skia.git',
                     patch_set=1,
                     patch_storage='gerrit') +
      api.path.exists(api.path['start_dir'].join('skp_output'))
  )

  buildername = 'Build-Debian9-GCC-x86_64-Release'
  yield (
      api.test('cross_repo_trybot') +
      api.properties(
          repository='https://skia.googlesource.com/parent_repo.git',
          buildername=buildername,
          path_config='kitchen',
          swarm_out_dir='[SWARM_OUT_DIR]',
          revision='abc123',
          patch_issue=500,
          patch_repo='https://skia.googlesource.com/skia.git',
          patch_set=1,
          patch_storage='gerrit') +
      api.properties.tryserver(
          buildername=buildername,
          gerrit_project='skia',
          gerrit_url='https://skia-review.googlesource.com/',
      ) +
      api.path.exists(
          api.path['start_dir'].join('tmp', 'uninteresting_hashes.txt')
      )
  )
  yield (
      api.test('trybot') +
      api.properties(buildername=buildername,
                     repository='https://skia.googlesource.com/skia.git',
                     revision='abc123',
                     path_config='kitchen',
                     patch_ref='refs/changes/89/456789/12',
                     patch_storage='gerrit',
                     swarm_out_dir='[SWARM_OUT_DIR]')
  )
