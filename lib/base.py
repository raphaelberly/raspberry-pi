# -*- coding: utf-8 -*-

from .tools import *
from bs4 import Tag, NavigableString


class Base:

    def __init__(self, base_type, config_folder):

        self._base_type = base_type
        self.config = read_config(os.path.join(config_folder, '{}.yaml'.format(base_type)))
        self.credentials = read_config(os.path.join(config_folder, 'credentials.yaml'))

    def get(self, item):
        return self.__getattribute__(item)

    def get_from_soup(self, base_soup, detail):
        soup = self.clone(base_soup)
        detail = self.config['find'][detail]
        soup = self._remove(soup, detail.get('remove'))
        soup = self._find(soup, detail.get('params'))
        soup = self._format(soup, detail.get('format'))
        soup = self._strip(soup, detail.get('strip'))
        return soup

    def _format_params(self, params):
        assert 'tag' in params, "'tag' key must be in {}".format(params)
        if params.get('type') and params.get('key'):
            return {'name': params.get('tag'), 'attrs': {params.get('type'): params.get('key')}}
        else:
            return {'name': params.get('tag')}

    def _remove(self, soup, remove):
        if not soup:
            return None
        if remove:
            if type(remove) == str:
                try:
                    soup.find(remove).extract()
                except AttributeError:
                    print('Warning: could not remove element: {}'.format(remove['key']))
            if type(remove) == dict:
                try:
                    soup.find(**self._format_params(remove)).extract()
                except AttributeError:
                    print('Warning: could not remove element: {}'.format(remove['key']))
            if type(remove) == list:
                # Remove each of the items of the to_remove list
                for item in remove:
                    soup.find(**self._format_params(item)).extract()
        return soup

    def _find(self, soup, params):
        if not soup:
            return None
        if type(params) == dict:
            if isinstance(soup, list):
                output = []
                for broth in soup:
                    if params.get('multiple'):
                        [output.append(item) for item in broth.findAll(**self._format_params(params))]
                    output.append(broth.find(**self._format_params(params)))
                return output
            else:
                if params.get('multiple'):
                    return soup.findAll(**self._format_params(params))
                return soup.find(**self._format_params(params))
        if type(params) == list:
            if isinstance(soup, list):
                output = []
                for broth in soup:
                    # Apply the filter one after the other
                    for param in params:
                        broth = self._find(broth, param)
                    output.extend(broth)
            else:
                output = soup
                # Apply the filter one after the other
                for param in params:
                    output = self._find(output, param)
            return output

    @staticmethod
    def _format(input, format):
        if not input:
            return None
        if format:
            if format == 'text':
                if isinstance(input, list):
                    return [item.text for item in input]
                return input.text
            else:
                if isinstance(input, list):
                    return [item[format] for item in input]
                return input[format]
        return input

    @staticmethod
    def _strip(input, strip):
        if not input:
            return None
        if strip:
            if isinstance(input, list):
                return [item.strip(strip) for item in input]
            return input.strip(strip)
        return input

    def clone(self, el):
        if isinstance(el, NavigableString):
            return type(el)(el)
        copy = Tag(None, el.builder, el.name, el.namespace, el.nsprefix)
        # work around bug where there is no builder set
        # https://bugs.launchpad.net/beautifulsoup/+bug/1307471
        copy.attrs = dict(el.attrs)
        for attr in ('can_be_empty_element', 'hidden'):
            setattr(copy, attr, getattr(el, attr))
        for child in el.contents:
            copy.append(self.clone(child))
        return copy
