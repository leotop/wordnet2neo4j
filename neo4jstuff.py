# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 15:03:08 2015

@author: sergey
"""

from py2neo import Graph
from py2neo import Node
from py2neo import Relationship
from py2neo import authenticate
        
class StuffNeo4j():
    
    def __init__(self, nodelabel, reltype):
        self.graph_db = None
        self.nodelabel = nodelabel
        self.reltype = reltype
        
    def connect(self, uri, usr="neo4j", pwd="neo4j"):
        if not uri.endswith('/'):
            uri += '/'
        authenticate(uri, usr, pwd)
        self.graph_db = Graph(uri + "db/data")
        
    def create_indexes(self):
        #If index is already created py2neo throws exception.
        try:
            self.graph_db.cypher.execute("CREATE INDEX ON :%s(name)" % 
                self.nodelabel)
        except:
            pass
        try:
            self.graph_db.cypher.execute("CREATE INDEX ON :%s(synset_id)" % 
                self.nodelabel)
        except:
            pass
        try:
            self.graph_db.cypher.execute("CREATE INDEX ON :%s(pointer_symbol)" %
                self.reltype)
        except:
            pass
    
    def create_node(self, nodetype, **kwargs):
        return Node(nodetype, **kwargs)
        
    def merge_node(self, nodetype, uniq_key, uniq_val, **kwargs):
        n = self.graph_db.merge_one(nodetype, uniq_key, uniq_val)
        for k in kwargs:        
            n.properties[k] = kwargs[k]
        n.push()
        return n
   
    def insert_rel(self, reltype, node1, node2, **kwargs):
        if node1 is not None and node2 is not None: 
            rel = Relationship(node1, reltype, node2, **kwargs)
            self.graph_db.create(rel)
        else:
            print "Could not insert relation (%s) - [%s] -> (%s)" % (           
                node1, reltype, node2)
            
    def merge_rel(self, reltype, node1, node2, **kwargs):
        if node1 is not None and node2 is not None: 
            rel = Relationship(node1, reltype, node2, **kwargs)
            return self.graph_db.create_unique(rel)
        else:
            print "Could not merge relation (%s) - [%s] -> (%s)" % (           
                node1, reltype, node2)
    
    def create_wordnet_rel(self, synset1, synset2, ptype):
        """
        Pointer symbols
        http://wordnet.princeton.edu/wordnet/man/wninput.5WN.html
        
         The pointer_symbol s for nouns are:
        
            !    Antonym
            @    Hypernym
            @i    Instance Hypernym
             ~    Hyponym
             ~i    Instance Hyponym
            #m    Member holonym
            #s    Substance holonym
            #p    Part holonym
            %m    Member meronym
            %s    Substance meronym
            %p    Part meronym
            =    Attribute
            +    Derivationally related form        
            ;c    Domain of synset - TOPIC
            -c    Member of this domain - TOPIC
            ;r    Domain of synset - REGION
            -r    Member of this domain - REGION
            ;u    Domain of synset - USAGE
            -u    Member of this domain - USAGE
        
        The pointer_symbol s for verbs are:
        
            !    Antonym
            @    Hypernym
             ~    Hyponym
            *    Entailment
            >    Cause
            ^    Also see
            $    Verb Group
            +    Derivationally related form        
            ;c    Domain of synset - TOPIC
            ;r    Domain of synset - REGION
            ;u    Domain of synset - USAGE
        
        The pointer_symbol s for adjectives are:
        
            !    Antonym
            &    Similar to
            <    Participle of verb
            \    Pertainym (pertains to noun)
            =    Attribute
            ^    Also see
            ;c    Domain of synset - TOPIC
            ;r    Domain of synset - REGION
            ;u    Domain of synset - USAGE
        
        The pointer_symbol s for adverbs are:
        
            !    Antonym
            \    Derived from adjective
            ;c    Domain of synset - TOPIC
            ;r    Domain of synset - REGION
            ;u    Domain of synset - USAGE 
        """
        node1 = self.graph_db.find_one(self.nodelabel, 
                                       property_key="synset_id",
                                       property_value=synset1)
        node2 = self.graph_db.find_one(self.nodelabel, 
                                       property_key="synset_id",
                                       property_value=synset2)
        if (node1 is not None) and (node2 is not None):
            rel = Relationship(node1, self.reltype, node2, pointer_symbol=ptype)
            return rel
        else:
            raise Exception("Could not create Wordnet relation (%s) - [%s] -> (%s)" % (           
                synset1, ptype, synset2))
        
    def insert_bulk(self, objs):
        if len(objs) > 0:
            self.graph_db.create(*objs)
