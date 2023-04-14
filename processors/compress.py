#   Copyright 2023 Google LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from .base import Processor, NotConfiguredException, ProcessorException
import os
import glob
import fnmatch
import zipfile
import tarfile


class CompressProcessor(Processor):
    """
    Compress files to zip/tar/tgz formats.

    Args:
        glob (str): Files to include, recursive. See Python glob().
        exclude (list, optional): List of files to exclude. See python fnmatch().
        output (str): Target file.
        format (str): One of: zip, tar, tar.gz, tar.bz2.
        compression (str, optional): Compression for ZIP: stored, bzip2, lzma. (default deflate)
        strip (int, optional): Remove N path parts in the archive.
    """

    def get_default_config_key():
        return 'compress'

    def process(self, output_var='compress'):
        if 'glob' not in self.config:
            raise NotConfiguredException('No files selected to be compressed.')
        if 'format' not in self.config:
            raise NotConfiguredException('Target archive format not specified.')
        if 'output' not in self.config:
            raise NotConfiguredException('No output file specified..')

        glob_spec = self._jinja_expand_string(self.config['glob'], 'glob')
        format_spec = self._jinja_expand_string(self.config['format'], 'format')
        output = self._jinja_expand_string(self.config['output'], 'output')
        strip = None
        if 'strip' in self.config:
            strip = int(self._jinja_expand_int(self.config['strip'], 'strip'))

        self._init_tempdir()
        directory = os.path.dirname(output)
        if directory and not os.path.exists(directory):
            self.logger.debug(
                'Creating directory under temporary directory: %s' %
                (directory))
            os.makedirs(directory, exist_ok=True)

        files_to_consider = glob.glob(glob_spec, recursive=True)
        if len(files_to_consider) == 0:
            self.logger.error('No files found to compress: %s' % (glob_spec),
                              extra={'glob': glob_spec})
            raise ProcessorException('No files found to compress')

        if 'exclude' in self.config:
            exclude_files = self._jinja_expand_list(self.config['exclude'],
                                                    'exclude')
            files = []
            for fname in files_to_consider:
                file_ok = True
                for exclude in exclude_files:
                    if fnmatch.fnmatch(fname, exclude):
                        file_ok = False
                        break
                if file_ok:
                    files.append(fname)
            if len(files) == 0:
                self.logger.error(
                    'No files found to compress after exclusion: %s' %
                    (glob_spec),
                    extra={'glob': glob_spec})
                raise ProcessorException(
                    'No files found to compress after exclusion')

        else:
            files = files_to_consider

        if format_spec == 'zip':
            zip_compression = zipfile.ZIP_DEFLATED
            if 'compression' in self.config:
                if self.config['compression'] == 'stored':
                    zip_compression = zipfile.ZIP_STORED
                elif self.config['compression'] == 'bzip2':
                    zip_compression = zipfile.ZIP_BZIP2
                elif self.config['compression'] == 'lzma':
                    zip_compression = zipfile.ZIP_LZMA

            self.logger.info('Compressing %d files to ZIP: %s' %
                             (len(files), output))
            zip_file = zipfile.ZipFile(output, 'x', zip_compression)
            for fname in files:
                target_name = fname
                if strip:
                    file_parts = fname.split(os.path.sep)
                    target_name = os.path.sep.join(file_parts[strip:])
                zip_file.write(fname, target_name)
            zip_file.close()
        elif format_spec == 'tar' or format_spec == 'tar.gz' or format_spec == 'tar.bz2' or format_spec == 'tar.xz':
            tar_mode = 'x:'
            if format_spec == 'tar.gz':
                tar_mode = 'x:gz'
            elif format_spec == 'tar.bz2':
                tar_mode = 'x:bz2'
            elif format_spec == 'tar.xz':
                tar_mode = 'x:xz'

            self.logger.info('Compressing %d files to %s: %s' %
                             (len(files), format_spec.upper(), output))

            tar_file = tarfile.open(output, tar_mode)
            for fname in files:
                target_name = fname
                if strip:
                    file_parts = fname.split(os.path.sep)
                    target_name = os.path.sep.join(file_parts[strip:])
                tar_file.add(fname, target_name)
            tar_file.close()

        file_stats = os.stat(output)
        return {
            output_var: {
                'path': output,
                'filename': os.path.basename(output),
                'format': format_spec,
                'size': file_stats.st_size,
            }
        }
