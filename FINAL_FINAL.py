#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 21:10:16 2019

@author: ajay
"""
import networkx as nx
import re
import nltk
import operator
class counterclass(object):
    def __init__(self, character_names): 
        self.list=character_names
        self.edge_count=1
class mainCharacters(object):
    def __init__(self,text):
        self.parseData=open(text ,'r').read()
        self.characters= re.findall(r'(?<=[a-z] )[A-Z][a-z]+', self.parseData)
        self.characters2= (re.findall(r'(?<=[a-z] )[A-Z][a-z]* [A-Z][a-z]*', self.parseData))
        #list of all cities
        self.cities= list(set(re.findall(r'[A-Z][a-z]* City', self.parseData)))
        self.funnel=[]
        self.counters=[]
        self.edges=[]
        self.d={}
    def sent_tokenize(self,text):
        #sentences = re.split(r"[.!?]", text)
        sentences = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', text)
        sentences = [sent.strip(" ") for sent in sentences]
        return sentences
    def pagerank(self,G, alpha=0.85,max_iter=100, tol=1.0e-6, weight='weight'):    
        if len(G) == 0:
            return {}
     
        # Create a copy in (right) stochastic form
        W = nx.stochastic_graph(G, weight=weight)
        N = W.number_of_nodes()
     
        # Choose fixed starting vector
        x = dict.fromkeys(W, 1.0 / N)
    
        # Assign uniform personalization vector if not given
        p = dict.fromkeys(W, 1.0 / N)
    
        dangling_weights = p
        dangling_nodes = [n for n in W if W.out_degree(n, weight=weight) == 0.0]
     
        # power iteration: make up to max_iter iterations
        for _ in range(max_iter):
            xlast = x
            x = dict.fromkeys(xlast.keys(), 0)
            danglesum = alpha * sum(xlast[n] for n in dangling_nodes)
            for n in x:
                # this matrix multiply looks odd because it is
                # doing a left multiply x^T=xlast^T*W
                for nbr in W[n]:
                    x[nbr] += alpha * xlast[n] * W[n][nbr][weight]
                x[n] += danglesum * dangling_weights[n] + (1.0 - alpha) * p[n]
     
            # check convergence, l1 norm
            err = sum([abs(x[n] - xlast[n]) for n in x])
            if err < N*tol:
                return x
                raise nx.NetworkXError('pagerank: power iteration failed to converge ''in %d iterations.' % max_iter)
    def findMain(self):
        greaterfinal=[]
        for i in range(len(self.characters)):
            count=self.characters.count(self.characters[i])
            #if character occurs over 45 times
            if count>20:
                greaterfinal.append(self.characters[i])
        for ch in greaterfinal:
            for city in self.cities:
                if ch==city:
                    greaterfinal.remove(ch)
        greaterfinal=set(greaterfinal)
        person_list=[]
        sentences=nltk.sent_tokenize(self.parseData)
        #maybe to make slower, instead of nested for loop throughtout entire parsedata, only look through greaterfinal
        for sentence in sentences:
            for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence))):
                if hasattr(chunk, 'label'):
                    if (chunk.label()=='PERSON') and (chunk.label()!='LOCATION' and chunk.label()!='NE'):
                        person_list.append(chunk[0][0])
        person_list=set(person_list)               
        # want to make this nested for loop UNNESTED for more efficiency
        self.funnel=list(person_list.intersection(greaterfinal)) 
        difference=set(greaterfinal-set(self.funnel))
        for ch in difference:
            count=self.characters.count(ch)
            if count>35:
                chunk=nltk.ne_chunk(nltk.pos_tag(ch))
                if(chunk.label()!='LOCATION'and chunk.label()!='NE'):
                    self.funnel.append(ch)
        #now test for two words
        greaterfinal2=[]
        for i in range(len(self.characters2)):
            count=self.characters2.count(self.characters2[i])
            if count>20:
                greaterfinal2.append(self.characters2[i])
        #print greaterfinal2
        greaterfinal2=list(set(greaterfinal2))
                
        for ch in greaterfinal2:
            words = re.split(r"[ ]", ch)
            for ch2 in self.funnel:
                if ch2==words[0] or ch2==words[1]:
                    self.funnel.remove(ch2)
                    chunk=nltk.ne_chunk(nltk.pos_tag(ch))
                    if(chunk.label()!='LOCATION'):
                        self.funnel.append(ch)  
        self.funnel=list(set(self.funnel))
        for i in range(len(self.funnel)):
            self.d.setdefault(i, [])
            self.d[i].append(self.funnel[i])
            words = self.funnel[i].split()
            if len(words)>1:
                for word in words:
                    self.d[i].append(word)
                    
        print self.funnel
    def edgeCounter(self): 
        sentences=self.sent_tokenize(self.parseData)
        # prints lists of names in each sentence, how many times that combo appears again
        for sentence in sentences:
            words = sentence.split()  # double-check this again when sentences list is accurate
            chars_in_sen=[]
            prev_word=words[0]
            for word in words:
                if word in self.funnel:
                    for key in self.d.keys():
                        if word in self.d[key]:
                            chars_in_sen.append(key)
                two_word = prev_word+' '+word
                if two_word in self.funnel:
                    for key in self.d.keys():
                        if two_word in self.d[key]:
                            chars_in_sen.append(key) 
                prev_word=word
                
            chars_in_sen = list(set(chars_in_sen))
            chars_in_sen.sort()
            if len(chars_in_sen)>1:
                match=0
                for counter in self.counters: #sifting through current edges
                     if chars_in_sen==counter.list: # if that characters in sentence already have an edge- should make this stronger by alphabetizing 
                        counter.edge_count+=1
                        match=1
                if match==0 or len(self.counters)<1: # no counter that matches
                    newcounter= counterclass(chars_in_sen)
                    self.counters.append(newcounter)  
    def edgeConnect(self):
        edgez=[]
        # creates counters for sets of 2 characters
        for character in self.d.keys():
            for character2 in self.d.keys():
                for counter in self.counters:
                    if (character in counter.list) and (character2 in counter.list) and (character!=character2):
                        match=0
                        for edge in edgez:
                            if (character in edge.list) and (character2 in edge.list):
                                edge.edge_count = counter.edge_count + edge.edge_count
                                match = 1 # found a match in an existing edge counter
                        if match==0: # no match in existing edges; make a new one
                            listy=[character,character2]
                            newcounter = counterclass(listy)
                            newcounter.edge_count=counter.edge_count
                            edgez.append(newcounter)    
        
        print "edges:"
        for edge in edgez:
            edge.edge_count=edge.edge_count/2
            for num in range(len(edge.list)):
                edge.list[num]=self.d[edge.list[num]][0]
        for edge in edgez:
            if edge.edge_count>3: #only display connections that occur more than 3 times
                self.edges.append(tuple(edge.list))

    def createGraph(self):
        #create graph
        self.findMain()
        self.edgeCounter()
        self.edgeConnect()
        G = nx.Graph()
        nodes = self.funnel
        G.add_nodes_from(nodes)
        G.add_edges_from(self.edges)
        pr = nx.pagerank(G, alpha=0.85) # the default damping parameter alpha = 0.85
        main_chars=[k for k in pr if pr[k]>0.05] # list of the main characters
        #draw network
        pos=nx.spring_layout(pr.keys(), scale = 4)
        nx.draw(G, pos, node_color='blue', node_size=[v*1000 for v in pr.values()], with_labels=True)
        #make important nodes green
        nx.draw_networkx_nodes(G, pos,node_color='green', nodelist=main_chars)





if __name__ == "__main__":
    #please enter full path directory of text file
    Script=mainCharacters('/Users/ajay/Desktop/wizard.txt')
    Script.createGraph()