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
    templates = { }
    self.preprocessor = make_parser( templates )

    from dw import make_parser
    self.parser = make_parser( )

  def parse( self, source ):

    if source[-1] != '\n':
      source += '\n'

    preprocessed_text = self.preprocessor.parse( source )
    tree = self.parser.parse( preprocessed_text.leaves( ))

    output = tree.leaves( )

    return output

#p = mw2dw.__init__( )
#import codecs
#fileObj = codecs.open("wikitext.txt", "r", "utf-8")
#source = fileObj.read( )
#output = p.parse( source )
#file( "article.txt", "w" ).write( output.encode( 'UTF-8' ))
