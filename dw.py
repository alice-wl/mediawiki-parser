from constants import html_entities
from mediawiki_parser import wikitextParser
from pijnu.library.node import Nil, Nodes, Node
import apostrophes
from pprint import pprint

def toolset( ):

    tags = {'bold': '**', 'bold_close': '**', 'italic': '//', 'italic_close': '//' }

    tags_stack = []

    external_autonumber = []
    """ This is for the autonumbering of external links.
    e.g.: "[http://www.mozilla.org] [http://fr.wikipedia.org]"
    is rendered as: "<a href="...">[1]</a> <a href="...">[2]</a>
    """
    category_links = []
    """ This will contain the links to the categories of the article. """

    namespaces = { 'Template':   'NS_TEMPLATE',
               'User':       'NS_USER',
               'Kategorie':  'NS_CATEGORY',
               'Category':   'NS_CATEGORY',
               'File':       'NS_FILE',
               'Image':      'NS_FILE',
	       'Talk':	     'NS_TALK' }

    def balance_tags(tag=None):
        i = 0
        if tag is not None:
            try:
                i = tags_stack.index(tag, -1)
            except ValueError:
                return ''
        result = ''
        while len(tags_stack) > i:
            result += '</%s>' % tags_stack.pop()
        return result

    def content(node):
        return apostrophes.parse('%s' % node.leaf() + balance_tags(), tags )

    def render_title1(node):
        node.value = '\n\n= %s\n' % node.leaf()

    def render_title2(node):
        node.value = '\n\n== %s\n' % node.leaf()

    def render_title3(node):
        node.value = '\n\n=== %s\n' % node.leaf()

    def render_title4(node):
        node.value = '\n\n==== %s\n' % node.leaf()

    def render_title5(node):
        node.value = '\n\n===== %s\n' % node.leaf()

    def render_title6(node):
        node.value = '\n\n====== %s\n' % node.leaf()

    def render_raw_text(node):
        pass

    def render_paragraph(node):
        node.value = '\n%s\n' % node.leaf()

    def render_wikitext(node):
        pass

    def render_body(node):
        metadata = ''
        #node.value = apostrophes.parse('%s' % node.leaves(), tags)

        try:
            if category_links != []:
                metadata+= '{{tag> '+ ','.join( category_links ) +'}}\n'
            if external_autonumber != []:
                i = 0
                external_autonumber.reverse( )
                while i <= len( external_autonumber):
                    i+= 1
                    metadata+= '* [%s] %s\n' % ( i, external_autonumber.pop( ))

            category_links = external_autonumber = []
            node.value+= metadata
            node.value = content(node) + metadata +"\n"

        except NameError:
            print "NameError"


    def render_entity(node):
        value = '%s' % node.leaf()
        if value in html_entities:
            node.value = '%s' % unichr(html_entities[value])
        else:
            node.value = '&%s;' % value

    def render_lt(node):
        pass

    def render_gt(node):
        pass

    def render_attribute(node):
        node.value = ''

    def render_tag_open(node):
        tag_name = node.value[0].value
        value = ''
        if tag_name == 'center':
            node.value = '<WRAP center>'
        elif tag_name == 'em':
            node.value = '<wrap em>'
	else:
            node.value = "<%s>" % tag_name

    def render_tag_close(node):
        tag_name = node.value[0].value
        if tag_name == 'center':
            tag = 'WRAP'
        elif tag_name == 'em':
            tag = 'wrap'
	else:
	    tag = tag_name

	node.value = "</%s>" % tag
	return

        node.value = '%s%s' % (tag_content, value)

    def render_tag_autoclose(node):
        tag_name = node.value[0].value
        value = attributes = ''
        if tag_name == 'p':
            node.value = '\n\n'
        elif tag_name == 'br':
            node.value = '\n\n'

    def render_table(node):
        table_parameters = ''
        table_content = ''
        if isinstance(node.value, Nodes) and node.value[0].tag == 'table_begin':
            contents = node.value[1].value
            for item in contents:
                table_content += content(item)
        else:
            table_content = content(node)
        node.value = '\n%s\n' % (table_content)
        pass

    def render_cell_content(node):
        if isinstance(node.value, Nil):
            return None
        cell_parameters = ''
        cell_content = ''
        if len(node.value) > 1:
            values = node.value[0].value
            for value in values:
                if isinstance(value, Node):
                    if value.tag == 'HTML_attribute' and value.value != '':
                        cell_parameters += ' ' + value.value
                    else:
                        cell_content += content( value.leaf())
                else:
                    cell_content += content( value )
            cell_content += content(node.value[1])
        else:
            cell_content = content(node)
	#print "cell: %s" % cell_content
        return ( cell_parameters, cell_content.replace( "\n", " " ) )

    def render_table_header_cell(node):
        #node.value = '^ %s  ' % node.leaf()
        result = ''
        if isinstance(node.value, Nodes):
            for i in range(len(node.value)):
                param, content = render_cell_content(node.value[i])
        else:
            param, content = render_cell_content(node)

        node.value = content

    def render_table_normal_cell( node ):
        result = ''
        if isinstance(node.value, Nodes):
            for i in range(len(node.value)):
                param, content = render_cell_content(node.value[i])
        else:
            param, content = render_cell_content(node)
        if content != '':
	    content = '| %s  ' % content
            node.value = content.replace("\n"," ")

    def render_table_empty_cell(node):
        node.value = '| '

    def render_table_caption(node):
        param, content = render_cell_content(node)
        if content is not None:
            node.value = '**%s**' % content

    def render_table_line_break(node):
        node.value = '|\n'


    def render_preformatted(node):
        node.value = '\n<code>' + content(node) +  '</code>\n'

    def render_hr(node):
        node.value = '----'

    def render_dd(list):
        pass

    def render_dt(list):
	pass

    def render_lists( list, d ):
        i = j = 0
	ret = ''
        while i < len(list):
	    if list[i].tag == 'bullet_list_leaf':
		ret+= '*' * d + ' %s\n' % content( list[i] ) 
	    elif list[i].tag == '@bullet_sub_list@':
		ret+= render_lists( list[i], d+1 )
	    if list[i].tag == 'number_list_leaf':
		ret+= '#' * d + ' %s\n' % content( list[i] ) 
	    elif list[i].tag == '@number_sub_list@':
		ret+= render_lists( list[i], d+1 )
	    if list[i].tag == 'colon_list_leaf':
		ret+= '*' * d + ' %s\n' % content( list[i] ) 
	    elif list[i].tag == '@colon_sub_list@':
		ret+= render_lists( list[i], d+1 )
	    if list[i].tag == 'semi_colon_list_leaf':
		ret+= '#' * d + ' %s\n' % content( list[i] ) 
	    elif list[i].tag == '@semi_colon_sub_list@':
		ret+= render_lists( list[i], d+1 )
            i += 1
	return ret

    def render_list( node ):
	node.value = render_lists( node.value, 1 )

    def render_url(node):
	text = node.value[0].leaf()
	node.value = '[[%s]]' % ( node.value[0].leaf( ))

    def render_external_link(node):
        if len(node.value) == 1:
	    link = node.leaf( )
	    if link not in external_autonumber:
		external_autonumber.append(node.leaf( ))
            node.value = '[[%s|%s]]' % ( link, len( external_autonumber ))
        else:
            text = node.value[1].leaf()
            node.value = '[[%s|%s]]' % ( node.value[0].leaf( ), text )

    def render_file(file_name, arguments):
	lfloat = ''; rfloat = ''; style=''
        if arguments != []:
            parameters = arguments[0].value
            for parameter in parameters:
                parameter = '%s' % parameter.leaf()
                if parameter[-2:] == 'px':
                    size = parameter[0:-2]
                    if 'x' in size:
                        size_x, size_y = size.split('x', 1)
                        try:
                            size_x = int(size_x)
                            size_y = int(size_y)
                            style += '?%sx%s' % (size_x, size_y)
                        except:
                            legend = parameter
                    else:
                        try:
                            size_x = int(size)
                            style += '?%s' % size_x
                        except:
                            legend = parameter
		elif parameter == 'left':
		    lfloat = ' '
		elif parameter == 'right':
		    rfloat = ' '
		elif parameter == 'center':
                    lfloat = ' '; rfloat = ' '
                else:
                    legend = parameter
        result = '{{%s%s%s%s}}' % ( lfloat, file_name, style, rfloat )
        return result

    def render_internal_link(node):
        url = ''
        page_name = node.value.pop(0).value
        if page_name[0] == ':':
            page_name = page_name[1:]
        if ':' in page_name:
            namespace, page_name = page_name.split(':', 1)
            if namespace in interwiki:
                url = interwiki[namespace]
                namespace = ''
            if namespace:
                page_name = namespace + ':' + page_name
        if len(node.value) == 0:
            text = page_name
        else:
            text = '|'.join('%s' % item.leaf() for item in node.value[0])
        node.value = '[[%s%s|%s]]' % (url, page_name, text)

    def render_internal_link(node):
        page_name = node.value.pop(0).value

        if page_name[0] == ':':
            page_name = page_name[1:]

        if ':' in page_name:
            namespace, page_name = page_name.split( ':', 1 )

            if namespace == 'Wikipedia':
		prefix, page = page_name.split( ':', 1 )
		node.value = '[[%s>%s]]' % ( prefix, page)
                return 
	    elif namespace in namespaces:
		if namespaces[namespace] == 'NS_FILE':
                    node.value = render_file( page_name, node.value )
                    return
		elif namespaces[namespace] == 'NS_TEMPLATE':
                    node.value = ''
                    return
		elif namespaces[namespace] == 'NS_CATEGORY':
		    if page_name not in category_links:
			category_links.append(page_name)
                    return
		else:
		    page_name = namespace + ':' + page_name

	    elif namespace:
                page_name = namespace + ':' + page_name
            else:
                page_name = '2012:' + page_name

	#link = make_internal_link( page_name )
	link = page_name.replace( '/', ':' )

        if len(node.value) != 0:
            text = '|'.join('%s' % item.leaf() for item in node.value[0])
	    node.value = '[[%s|%s]]' % (link, text)
	else:
	    node.value = '[[%s]]' % (link)

    return locals()

def make_internal_link( link ):
    return link

def make_parser( ):
    tools = toolset( )
    return wikitextParser.make_parser( tools )
