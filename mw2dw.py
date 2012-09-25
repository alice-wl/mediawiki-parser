# -*- coding: utf8 -*-
import os

# get the parser
class mw2dw:
  def __init__( self ):
    from pijnu import makeParser
    path, script = os.path.realpath(__file__).rsplit( '/' , 1 )
    preprocessorGrammar = file( path+"/preprocessor.pijnu" ).read( )
    makeParser( preprocessorGrammar )

    mediawikiGrammar = file( path+"/mediawiki.pijnu" ).read( )
    makeParser( mediawikiGrammar )

    from preprocessor import make_parser
    ## FIXME dataentry interferes with mediawiki syntax and ist parsed as such
    ## FIXME NUMBEROFARTICLES does not work at all
    templates = { 'An-Ja': u'X ', 'An-Nein': u'-', 'Team': u"""<nowiki>---- dataentry Team ----</nowiki>\n\nname : {{{NAME}}}\n\ncoordinator : {{{COORDINATOR|}}}\n\nroom : {{{ROOM}}}\n\nnumber : {{{PHONE}}}\n\n----\n\n{{topic>{{{TEAM}}}}}\n\n""", 'NUMBEROFARTICLES': '{{template:numberofarticles}}' }

    self.preprocessor = make_parser( templates )

    from dw import make_parser
    self.parser = make_parser( )
    ## FIXME should do all the namespace stuff here


  def parse( self, source ):

    if len( source ) and source[-1] != '\n':
      source += '\n'

    preprocessed_text = self.preprocessor.parse( source )
    tree = self.parser.parse( preprocessed_text.leaves( ))

    output = tree.leaves( )

    return output
